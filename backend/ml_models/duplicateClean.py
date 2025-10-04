import pandas as pd

# List of your files
files = ["misinformations.csv", "sentiment_dataset.csv", "toxic.csv"]

for file in files:
    print(f"Cleaning {file}...")

    # Load CSV
    df = pd.read_csv(file)

    # Normalize column names (strip spaces + lowercase)
    df.columns = df.columns.str.strip().str.lower()

    # Try to find the "text" column
    if "text" not in df.columns:
        print(f"❌ No 'text' column found in {file}. Available columns: {list(df.columns)}")
        continue

    # Remove duplicates in "text" column
    before = len(df)
    df = df.drop_duplicates(subset=["text"])
    after = len(df)

    # Overwrite same file
    df.to_csv(file, index=False)

    print(f"✅ {file} updated. Removed {before - after} duplicates (kept {after} rows).")

print("🎉 All files cleaned successfully!")
