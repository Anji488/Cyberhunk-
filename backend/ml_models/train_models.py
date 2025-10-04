import os
import logging
import pandas as pd
import json
import shutil
import psutil  # for checking disk space
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    Trainer,
    TrainingArguments,
    DataCollatorForTokenClassification
)

# ------------------------
# Logging
# ------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------
# Paths
# ------------------------
DATA_DIR = "./datasets"
MODEL_DIR = "./models"
LOG_DIR = "./logs"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ------------------------
# Datasets and Models
# ------------------------
dataset_files = {
    "sentiment": os.path.join(DATA_DIR, "sentiment_dataset.csv"),
    "toxicity": os.path.join(DATA_DIR, "toxic.csv"),
    "misinformation": os.path.join(DATA_DIR, "misinformations.csv"),
    "ner": os.path.join(DATA_DIR, "ner_locations.json"),
}

model_names = {
    "sentiment": "roberta-base",
    "toxicity": "unitary/toxic-bert",
    "misinformation": "bert-base-uncased",
    "ner": "bert-base-cased"
}

num_labels = {
    "sentiment": 3,
    "toxicity": 2,
    "misinformation": 2,
    "ner": 2
}

# ------------------------
# Checkpoints and Cleanup
# ------------------------
KEEP_LAST_N = 2

def is_checkpoint_valid(ckpt_path):
    required_files = ["config.json", "trainer_state.json", "training_args.bin"]
    weight_files = ["pytorch_model.bin", "model.safetensors"]

    missing = [f for f in required_files if not os.path.exists(os.path.join(ckpt_path, f))]
    weight_ok = any(
        os.path.exists(os.path.join(ckpt_path, wf)) and os.path.getsize(os.path.join(ckpt_path, wf)) > 0
        for wf in weight_files
    )
    return not missing and weight_ok

def cleanup_checkpoints(task_dir, keep_last_n=KEEP_LAST_N):
    if not os.path.isdir(task_dir):
        return
    checkpoints = [d for d in os.listdir(task_dir) if d.startswith("checkpoint-")]
    if not checkpoints:
        return

    checkpoints = sorted(checkpoints, key=lambda x: int(x.split("-")[-1]))
    valid_checkpoints = []

    for ckpt in checkpoints:
        ckpt_path = os.path.join(task_dir, ckpt)
        if is_checkpoint_valid(ckpt_path):
            valid_checkpoints.append(ckpt)
        else:
            logger.info(f"Deleting corrupted checkpoint: {ckpt_path}")
            shutil.rmtree(ckpt_path, ignore_errors=True)

    # Delete older valid checkpoints
    if len(valid_checkpoints) > keep_last_n:
        to_delete = valid_checkpoints[:-keep_last_n]
        for ckpt in to_delete:
            ckpt_path = os.path.join(task_dir, ckpt)
            logger.info(f"Deleting old valid checkpoint: {ckpt_path}")
            shutil.rmtree(ckpt_path, ignore_errors=True)

def get_last_valid_checkpoint(task_dir):
    if not os.path.isdir(task_dir):
        return None
    checkpoints = [d for d in os.listdir(task_dir) if d.startswith("checkpoint-")]
    if not checkpoints:
        return None
    checkpoints = sorted(checkpoints, key=lambda x: int(x.split("-")[-1]), reverse=True)
    for ckpt in checkpoints:
        ckpt_path = os.path.join(task_dir, ckpt)
        if is_checkpoint_valid(ckpt_path):
            return ckpt_path
    return None

# ------------------------
# Disk Space Check
# ------------------------
def check_disk_space(min_gb=10):
    """Check if free disk space is above min_gb"""
    disk = psutil.disk_usage(".")
    free_gb = disk.free / 1024**3
    if free_gb < min_gb:
        logger.warning(f"Low disk space: {free_gb:.2f} GB free")
        return False
    return True

# ------------------------
# Training Function
# ------------------------
def train_model(task_name):
    file_path = dataset_files[task_name]
    if not os.path.exists(file_path):
        logger.warning(f"No dataset found for {task_name}: {file_path}")
        return

    output_dir = os.path.join(MODEL_DIR, task_name)
    os.makedirs(output_dir, exist_ok=True)

    # Cleanup old checkpoints first
    cleanup_checkpoints(output_dir, KEEP_LAST_N)

    # Ensure enough disk space
    if not check_disk_space(min_gb=10):
        logger.info(f"Attempting to cleanup old checkpoints to free space for {task_name}...")
        cleanup_checkpoints(output_dir, KEEP_LAST_N)
        if not check_disk_space(min_gb=10):
            logger.error(f"Not enough disk space to train {task_name}. Please free up space.")
            return

    logger.info(f"Training {task_name} model using {file_path} ...")

    # ------------------------
    # Non-NER tasks
    # ------------------------
    if task_name != "ner":
        df = pd.read_csv(file_path)
        if "text" not in df.columns:
            df = df.rename(columns={df.columns[0]: "text"})
        df = df.dropna(subset=["text"])

        if "label" in df.columns:
            if df["label"].dtype == object:
                if task_name == "sentiment":
                    label_map = {"negative": 0, "neutral": 1, "positive": 2}
                else:
                    label_map = {False: 0, True: 1, "0": 0, "1": 1}
                df["label"] = df["label"].apply(lambda x: label_map.get(str(x).lower(), 0))
        dataset = Dataset.from_pandas(df)

        tokenizer = AutoTokenizer.from_pretrained(model_names[task_name])
        model = AutoModelForSequenceClassification.from_pretrained(
            model_names[task_name],
            num_labels=num_labels[task_name]
        )

        def tokenize(batch):
            texts = [str(t) for t in batch["text"]]
            return tokenizer(texts, padding=True, truncation=True, max_length=128)

        train_dataset = dataset.map(tokenize, batched=True)
        eval_dataset = train_dataset
        data_collator = None

    # ------------------------
    # NER task
    # ------------------------
    else:
        with open(file_path, "r") as f:
            data = json.load(f)
        dataset = Dataset.from_dict({
            "tokens": [x["tokens"] for x in data["train"]],
            "ner_tags": [x["ner_tags"] for x in data["train"]]
        })

        tokenizer = AutoTokenizer.from_pretrained(model_names[task_name])
        model = AutoModelForTokenClassification.from_pretrained(
            model_names[task_name],
            num_labels=num_labels[task_name]
        )

        def tokenize_and_align_labels(examples):
            tokenized_inputs = tokenizer(
                examples["tokens"],
                is_split_into_words=True,
                truncation=True,
                padding="max_length",
                max_length=128
            )
            labels = []
            for i, label in enumerate(examples["ner_tags"]):
                word_ids = tokenized_inputs.word_ids(batch_index=i)
                label_ids = []
                previous_word_idx = None
                for word_idx in word_ids:
                    if word_idx is None:
                        label_ids.append(-100)
                    elif word_idx != previous_word_idx:
                        label_ids.append(label[word_idx])
                    else:
                        label_ids.append(label[word_idx])
                    previous_word_idx = word_idx
                labels.append(label_ids)
            tokenized_inputs["labels"] = labels
            return tokenized_inputs

        train_dataset = dataset.map(tokenize_and_align_labels, batched=True)
        eval_dataset = train_dataset
        data_collator = DataCollatorForTokenClassification(tokenizer)

    # ------------------------
    # Training Arguments
    # ------------------------
    training_args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        logging_dir=os.path.join(LOG_DIR, task_name),
        save_strategy="steps",
        save_steps=1000,
        save_total_limit=KEEP_LAST_N,
        logging_steps=100,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator
    )

    last_checkpoint = get_last_valid_checkpoint(output_dir)
    if last_checkpoint:
        logger.info(f"Resuming {task_name} from last valid checkpoint: {last_checkpoint}")
        trainer.train(resume_from_checkpoint=last_checkpoint)
    else:
        trainer.train()

    trainer.save_model(output_dir)
    logger.info(f"Saved {task_name} model to {output_dir}")

# ------------------------
# Train all tasks safely
# ------------------------
for task in dataset_files.keys():
    train_model(task)

logger.info("All models trained successfully!")
