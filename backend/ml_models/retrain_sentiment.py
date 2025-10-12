# retrain_sentiment.py
import pandas as pd
import emoji
import random
import torch
import nltk
from nltk.corpus import wordnet, stopwords
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import precision_recall_fscore_support
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)

# Optional imports for backtranslation
try:
    from transformers import MarianMTModel, MarianTokenizer
    import sentencepiece
    SENTENCEPIECE_AVAILABLE = True
except ImportError:
    print("⚠️ sentencepiece not installed. Backtranslation disabled.")
    SENTENCEPIECE_AVAILABLE = False

nltk.download('wordnet')
nltk.download('stopwords')

# ==============================
# Load Translation Models (Optional)
# ==============================
if SENTENCEPIECE_AVAILABLE:
    try:
        tokenizer_en_fr = MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-en-fr')
        model_en_fr = MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-en-fr')
        tokenizer_fr_en = MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-fr-en')
        model_fr_en = MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-fr-en')
        BACKTRANSLATE_AVAILABLE = True
    except Exception as e:
        print(f"⚠️ Could not load translation models: {e}")
        BACKTRANSLATE_AVAILABLE = False
else:
    BACKTRANSLATE_AVAILABLE = False

stop_words = set(stopwords.words('english'))

# ==============================
# Emoji Conversion
# ==============================
def convert_emojis_to_words(text):
    return emoji.demojize(str(text), delimiters=(" ", " "))

# ==============================
# Synonym Replacement
# ==============================
def synonym_replacement(text, n=2):
    words = text.split()
    new_words = words.copy()
    candidates = [w for w in set(words) if w.isalpha() and w.lower() not in stop_words]
    random.shuffle(candidates)
    replaced = 0
    for word in candidates:
        synonyms = wordnet.synsets(word)
        lemmas = set(l.name().replace('_', ' ') for s in synonyms for l in s.lemmas())
        lemmas.discard(word)
        if lemmas:
            replacement = random.choice(list(lemmas))
            new_words = [replacement if w == word else w for w in new_words]
            replaced += 1
        if replaced >= n:
            break
    return ' '.join(new_words)

# ==============================
# Backtranslation
# ==============================
def backtranslate_text(text):
    if not BACKTRANSLATE_AVAILABLE:
        return text
    try:
        fr = model_en_fr.generate(**tokenizer_en_fr([text], return_tensors="pt", padding=True))
        fr_text = tokenizer_en_fr.decode(fr[0], skip_special_tokens=True)
        en = model_fr_en.generate(**tokenizer_fr_en([fr_text], return_tensors="pt", padding=True))
        return tokenizer_fr_en.decode(en[0], skip_special_tokens=True)
    except Exception:
        return text

# ==============================
# Load Dataset
# ==============================
def load_dataset(file_path, text_col="text", label_col="label"):
    df = pd.read_csv(file_path)
    df = df.dropna(subset=[text_col, label_col])
    df[text_col] = df[text_col].apply(convert_emojis_to_words)
    return df

# ==============================
# Balance Classes
# ==============================
def balance_classes(df, label_col="label"):
    max_size = df[label_col].value_counts().max()
    lst = [df]
    for _, group in df.groupby(label_col):
        lst.append(group.sample(max_size - len(group), replace=True))
    df_balanced = pd.concat(lst).sample(frac=1).reset_index(drop=True)
    return df_balanced

# ==============================
# Encode Labels
# ==============================
def encode_labels(df, label_col="label"):
    le = LabelEncoder()
    df[label_col] = le.fit_transform(df[label_col])
    return df, le

# ==============================
# Data Augmentation
# ==============================
def augment_dataset(df, text_col="text", label_col="label", n_aug=1, backtranslate=False):
    augmented_texts, augmented_labels = [], []
    for _, row in df.iterrows():
        text, label = row[text_col], row[label_col]
        augmented_texts.append(text)
        augmented_labels.append(label)
        for _ in range(n_aug):
            aug_text = synonym_replacement(text)
            augmented_texts.append(aug_text)
            augmented_labels.append(label)
        if backtranslate and BACKTRANSLATE_AVAILABLE:
            bt_text = backtranslate_text(text)
            augmented_texts.append(bt_text)
            augmented_labels.append(label)
    return pd.DataFrame({text_col: augmented_texts, label_col: augmented_labels})

# ==============================
# Metrics
# ==============================
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = torch.argmax(torch.tensor(logits), dim=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    accuracy = (preds == torch.tensor(labels)).float().mean()
    return {
        "accuracy": accuracy.item(),
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

# ==============================
# Train Transformer
# ==============================
def train_transformer(df, model_name="distilbert-base-uncased", output_path="model"):
    dataset = Dataset.from_pandas(df)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize(batch):
        return tokenizer(batch["text"], padding=True, truncation=True, max_length=128)

    dataset = dataset.map(tokenize, batched=True)
    dataset = dataset.train_test_split(test_size=0.2)

    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(df["label"].unique())
    )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"📌 Training on device: {device}")

    # Backward-compatible TrainingArguments
    training_args = TrainingArguments(
        output_dir=f"./{output_path}",
        do_eval=True,
        eval_steps=500,
        save_steps=500,
        logging_steps=50,
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=4,
        weight_decay=0.01
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        compute_metrics=compute_metrics,
        tokenizer=tokenizer
    )

    trainer.train()
    trainer.save_model(f"./{output_path}")
    tokenizer.save_pretrained(f"./{output_path}")
    print(f"✅ Model saved to {output_path}")

# ==============================
# Main
# ==============================
if __name__ == "__main__":
    tasks = [
        ("sentiment_dataset.csv", "bert_sentiment"),
        ("toxic.csv", "bert_toxic"),
        ("misinformations.csv", "bert_misinformation")
    ]

    for file, name in tasks:
        print(f"\n🚀 Training model: {name}")
        df = load_dataset(file)
        df = balance_classes(df)
        df = augment_dataset(df, n_aug=2, backtranslate=True)
        df, _ = encode_labels(df)
        train_transformer(df, output_path=name)
