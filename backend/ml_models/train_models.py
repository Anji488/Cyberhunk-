import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import make_pipeline
import joblib
import os

# Folder where your CSVs are located
data_folder = os.path.join(os.path.dirname(__file__))

# List of CSV files you want to train models on
csv_files = [
    'misinfromations.csv',
    'toxic.csv',
    'sentiment_dataset.csv'
]

# Common possible column names for text and label
text_columns = ['text', 'comment', 'sentence', 'review']
label_columns = ['label', 'toxicity', 'sentiment', 'class']

for csv_name in csv_files:
    csv_path = os.path.join(data_folder, csv_name)
    print(f"Training model for {csv_name}...")

    # Load dataset
    try:
        data = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"File not found: {csv_path}, skipping.\n")
        continue

    # Case-insensitive detection of text and label columns
    data_columns_lower = [c.lower() for c in data.columns]

    text_col = next(
        (data.columns[i] for i, c in enumerate(data_columns_lower) if c in [t.lower() for t in text_columns]),
        None
    )
    label_col = next(
        (data.columns[i] for i, c in enumerate(data_columns_lower) if c in [l.lower() for l in label_columns]),
        None
    )

    if text_col is None or label_col is None:
        print(f"Skipping {csv_name}: could not detect text or label column.")
        print(f"Available columns: {data.columns.tolist()}\n")
        continue

    # Clean data
    data = data.dropna(subset=[text_col, label_col])
    data[text_col] = data[text_col].astype(str)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        data[text_col], data[label_col], test_size=0.2, random_state=42
    )

    # Build and train model
    model = make_pipeline(CountVectorizer(), MultinomialNB())
    model.fit(X_train, y_train)

    # Evaluate
    accuracy = model.score(X_test, y_test)
    print(f"Accuracy for {csv_name}: {accuracy:.4f}")

    # Save model
    model_file = os.path.splitext(csv_name)[0] + '_model.pkl'
    model_path = os.path.join(data_folder, model_file)
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}\n")
