import pandas as pd
import json
import os

# ------------------------
# Paths
# ------------------------
DATA_DIR = "./datasets"
LOC_FILE = os.path.join(DATA_DIR, "locations.csv")      # Input CSV
NER_FILE = os.path.join(DATA_DIR, "ner_locations.json") # Output JSON

# ------------------------
# Load locations
# ------------------------
df = pd.read_csv(LOC_FILE)
locations = []
for _, row in df.iterrows():
    locations.append({"city": row["city"], "country": row["country"]})

print(f"Total locations loaded: {len(locations)}")

# ------------------------
# Generate NER examples
# ------------------------
examples = []

for loc in locations:
    # Sentence with the city
    sent_tokens = ["I", "visited", loc["city"], "last", "year", "."]
    ner_tags = [0, 0, 1, 0, 0, 0]  # 1 = LOC for city
    
    examples.append({"tokens": sent_tokens, "ner_tags": ner_tags})
    
    # Sentence with the country
    sent_tokens = ["I", "traveled", "to", loc["country"], "last", "year", "."]
    ner_tags = [0, 0, 0, 1, 0, 0, 0]  # 1 = LOC for country
    
    examples.append({"tokens": sent_tokens, "ner_tags": ner_tags})

# ------------------------
# Train/test split
# ------------------------
split = int(len(examples) * 0.8)
ner_dataset = {
    "train": examples[:split],
    "test": examples[split:]
}

# ------------------------
# Save as JSON
# ------------------------
with open(NER_FILE, "w") as f:
    json.dump(ner_dataset, f, indent=2)

print(f"NER dataset created: {NER_FILE}")
print(f"Train examples: {len(ner_dataset['train'])}, Test examples: {len(ner_dataset['test'])}")
