import os
import shutil

MODEL_DIR = "./models"
KEEP_LAST_N = 2  # number of valid checkpoints to keep per task

def is_checkpoint_valid(ckpt_path):
    """
    Check if a checkpoint folder has required files and valid model weights.
    """
    required_files = ["config.json", "trainer_state.json", "training_args.bin"]
    weight_files = ["pytorch_model.bin", "model.safetensors"]

    # Check required files
    missing = [f for f in required_files if not os.path.exists(os.path.join(ckpt_path, f))]

    # Check if at least one weight file exists and is non-empty
    weight_ok = any(
        os.path.exists(os.path.join(ckpt_path, wf)) and os.path.getsize(os.path.join(ckpt_path, wf)) > 0
        for wf in weight_files
    )

    return not missing and weight_ok

def validate_and_cleanup(model_dir=MODEL_DIR, keep_last_n=KEEP_LAST_N):
    if not os.path.exists(model_dir):
        print(f"No model directory found at {model_dir}")
        return

    for task_name in os.listdir(model_dir):
        task_path = os.path.join(model_dir, task_name)
        if not os.path.isdir(task_path):
            continue

        checkpoints = [d for d in os.listdir(task_path) if d.startswith("checkpoint-")]
        if not checkpoints:
            continue

        # Sort checkpoints numerically
        checkpoints = sorted(checkpoints, key=lambda x: int(x.split("-")[-1]))
        valid_checkpoints = []

        # Validate each checkpoint
        for ckpt in checkpoints:
            ckpt_path = os.path.join(task_path, ckpt)
            if is_checkpoint_valid(ckpt_path):
                print(f"✅ {ckpt} is valid")
                valid_checkpoints.append(ckpt)
            else:
                print(f"❌ {ckpt} is CORRUPTED, will be deleted")
                shutil.rmtree(ckpt_path, ignore_errors=True)

        # Delete old valid checkpoints, keep only last N
        if len(valid_checkpoints) > keep_last_n:
            to_delete = valid_checkpoints[:-keep_last_n]
            for ckpt in to_delete:
                ckpt_path = os.path.join(task_path, ckpt)
                print(f"🗑️ Deleting old valid checkpoint: {ckpt_path}")
                shutil.rmtree(ckpt_path, ignore_errors=True)

        if valid_checkpoints[-keep_last_n:]:
            print(f"✅ Kept last {keep_last_n} valid checkpoints for {task_name}: {valid_checkpoints[-keep_last_n:]}")

if __name__ == "__main__":
    validate_and_cleanup()
