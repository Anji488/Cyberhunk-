# evaluate_all_models.py
import joblib
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score

# ==============================
# Helper function to clean dataset
# ==============================
def clean_dataset(df, text_col="text", label_col="label"):
    # Fill missing text and labels
    df[text_col] = df[text_col].fillna("").str.strip()
    df[label_col] = df[label_col].fillna("unknown").astype(str).str.lower().str.strip()

    # Remove empty text and unknown labels
    df = df[(df[text_col] != "") & (df[label_col] != "unknown")]
    return df

# ==============================
# Evaluate model and show misclassified samples
# ==============================
def evaluate_model(model_path, dataset_path, model_name, text_col="text", label_col="label", show_misclassified=True, max_samples=5):
    try:
        # Load model and dataset
        model = joblib.load(model_path)
        df = pd.read_csv(dataset_path)
        df = clean_dataset(df, text_col, label_col)

        X_test = df[text_col]
        y_test = df[label_col]

        # Predict
        y_pred = model.predict(X_test)

        # Accuracy & report
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\n✅ {model_name} Accuracy: {accuracy:.2%}")
        print(f"--- {model_name} Classification Report ---")
        print(classification_report(y_test, y_pred, zero_division=0))

        # Show misclassified samples
        if show_misclassified:
            misclassified = df[y_test != y_pred].copy()
            misclassified["predicted"] = y_pred[y_test != y_pred]
            if not misclassified.empty:
                print(f"\n--- Sample Misclassified {model_name} ---")
                print(misclassified[[text_col, label_col, "predicted"]].head(max_samples))
            else:
                print(f"\nNo misclassified samples found for {model_name}.")

    except FileNotFoundError as e:
        print(f"⚠️ {model_name} dataset or model file not found: {e}")
    except Exception as e:
        print(f"⚠️ Error evaluating {model_name}: {e}")

# ==============================
# Evaluate all models
# ==============================
# 1️⃣ Sentiment Model
evaluate_model(
    model_path="sentiment_dataset_model.pkl",
    dataset_path="sentiment_dataset.csv",
    model_name="Sentiment Model"
)

# 2️⃣ Toxic Model
evaluate_model(
    model_path="toxic_model.pkl",
    dataset_path="toxic.csv",
    model_name="Toxic Model",
    text_col="Text",  
    label_col="label"
)

# 3️⃣ Misinformation Model
evaluate_model(
    model_path="misinformations_model.pkl",
    dataset_path="misinformations.csv",
    model_name="Misinformation Model",
    text_col="text",
    label_col="label"
)
