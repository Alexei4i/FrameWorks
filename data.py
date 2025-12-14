
# Simple COVID-19 Metadata Analysis Script

import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import Counter

# --- STEP 1: LOAD THE DATA ---
print("Loading data...")

try:
    data = pd.read_csv(r"c:\Users\user\PLP\Python\Python FrameWorks\Python_FrameWorks_Assignment\metadata.csv")
    print("✅ Data loaded successfully!")
except FileNotFoundError:
    print("❌ Error: 'metadata.csv' not found in this folder.")
    exit()

# --- STEP 2: QUICK LOOK AT THE DATA ---

print("\nFirst few rows:")
print(data.head())

print("\nData info:")
print(data.info())

print("\nMissing values in key columns:")
key_columns = ["title", "abstract", "journal", "publish_time"]
print(data[key_columns].isnull().sum())

# --- STEP 3: BASIC CLEANING ---

print("\nCleaning data...")

# Drop rows that don’t have a title or publish date
cleaned = data.dropna(subset=["title", "publish_time"]).copy()

# Replace missing abstracts and journals with placeholders
cleaned["abstract"] = cleaned["abstract"].fillna("NO ABSTRACT PROVIDED")
cleaned["journal"] = cleaned["journal"].fillna("UNKNOWN JOURNAL")

# Convert publish_time to datetime format
cleaned["publish_date"] = pd.to_datetime(cleaned["publish_time"], errors="coerce")
cleaned = cleaned.dropna(subset=["publish_date"])  # Drop rows where date is invalid

# Extract publication year
cleaned["year"] = cleaned["publish_date"].dt.year

print(f"✅ Data cleaned! Remaining rows: {len(cleaned)}")

# --- STEP 4: SIMPLE ANALYSIS ---

# Count how many papers were published each year
year_counts = cleaned["year"].value_counts().sort_index()
print("\nPapers published per year:")
print(year_counts)

# Top 10 journals
top_journals = cleaned["journal"].value_counts().head(10)
print("\nTop 10 journals:")
print(top_journals)

# --- STEP 5: WORD FREQUENCY IN TITLES ---

print("\nFinding most common words in paper titles...")

# Combine all titles into one long string
all_titles = " ".join(cleaned["title"].astype(str).str.lower())

# Remove punctuation and split into words
words = re.findall(r'\b\w+\b', all_titles)

# Define a small list of common words to ignore
stop_words = {"the", "and", "of", "in", "a", "to", "on", "for", 
              "with", "an", "by", "at", "from", "about", "study", 
              "covid", "19", "coronavirus", "analysis", "research"}

# Filter words
filtered = [w for w in words if w not in stop_words and len(w) > 2]

# Count top 15 most frequent words
top_words = Counter(filtered).most_common(15)
print("\nTop 15 words in titles:")
for word, count in top_words:
    print(f"{word}: {count}")

# --- STEP 6: VISUALIZATIONS ---

plt.style.use("ggplot")

# 1. Bar chart - number of papers per year
plt.figure(figsize=(8, 5))
year_counts.plot(kind="bar", color="skyblue")
plt.title("Number of Publications per Year")
plt.xlabel("Year")
plt.ylabel("Number of Papers")
plt.tight_layout()

# Save the figure before showing
plt.savefig("papers_per_year.png", dpi=300)
print("📊 Saved: papers_per_year.png")

plt.show()

# 2. Horizontal bar chart - top journals
plt.figure(figsize=(10, 6))
top_journals.sort_values().plot(kind="barh", color="teal")
plt.title("Top 10 Journals Publishing COVID-19 Papers")
plt.xlabel("Number of Papers")
plt.ylabel("Journal")
plt.tight_layout()

# Save the figure before showing
plt.savefig("top_journals.png", dpi=300)
print("📊 Saved: top_journals.png")

plt.show()

# --- STEP 7: SAVE CLEANED DATA ---

cleaned.to_csv("cleaned_metadata.csv", index=False)
print("\n✅ Cleaned data saved as 'cleaned_metadata.csv'")
print("🎉 Analysis complete!")
