import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import Counter

# Set page to wide mode for better layout
st.set_page_config(layout="wide")

# --- STEP 1, 2, 3: LOAD AND CLEAN DATA (CACHED) ---
@st.cache_data  # This decorator caches the result, so data is loaded only once.
def load_and_clean_data():
    """
    Loads and cleans the metadata.csv file.
    All print statements are removed and cleaning logic is combined.
    """
    try:
        # Load the data. Assumes "metadata.csv" is in the same folder.
        data = pd.read_csv("metadata.csv", low_memory=False)
    except FileNotFoundError:
        st.error("❌ Error: 'metadata.csv' not found.")
        st.info("Please place 'metadata.csv' in the same folder as this 'app.py' script.")
        st.stop()  # Stop the script execution

    # --- Cleaning (from your original script) ---
    # Drop rows that don’t have a title or publish date
    cleaned = data.dropna(subset=["title", "publish_time"]).copy()

    # Replace missing abstracts and journals with placeholders
    cleaned["abstract"] = cleaned["abstract"].fillna("NO ABSTRACT PROVIDED")
    cleaned["journal"] = cleaned["journal"].fillna("UNKNOWN JOURNAL")

    # Convert publish_time to datetime format
    cleaned["publish_date"] = pd.to_datetime(cleaned["publish_time"], errors="coerce")
    cleaned = cleaned.dropna(subset=["publish_date"])  # Drop rows where date is invalid

    # Extract publication year as an integer
    cleaned["year"] = cleaned["publish_date"].dt.year.astype(int)
    
    return cleaned

# Load the data
data = load_and_clean_data()

# --- STREAMLIT APP LAYOUT ---

st.title("CORD-19 Data Explorer")
st.write("Simple exploration of COVID-19 research papers. Data is filtered by the options you select in the sidebar.")

# --- SIDEBAR WITH INTERACTIVE WIDGETS ---
st.sidebar.header("Filter Options")

# Get min and max year from the data for the slider
min_year = data["year"].min()
max_year = data["year"].max()

# 1. Year Range Slider
year_range = st.sidebar.slider(
    "Select year range",
    min_year,
    max_year,
    (min_year, max_year)  # Default to the full range
)

# 2. Top N Slider for Journals
top_n_journals = st.sidebar.slider(
    "Select Top N Journals",
    5, 25, 10  # min, max, default
)

# 3. Top N Slider for Words
top_n_words = st.sidebar.slider(
    "Select Top N Words in Titles",
    5, 30, 15  # min, max, default
)

# --- FILTER DATA BASED ON SELECTIONS ---
filtered_data = data[
    (data["year"] >= year_range[0]) & (data["year"] <= year_range[1])
]

st.header(f"Analysis for {year_range[0]}–{year_range[1]}")
st.markdown(f"Found **{len(filtered_data)}** articles in the selected period.")

# --- STEP 4 & 6: DYNAMIC ANALYSIS AND VISUALIZATIONS ---

# Use columns for a side-by-side layout
col1, col2 = st.columns(2)

with col1:
    # --- 1. Bar chart - number of papers per year ---
    st.subheader("Publications per Year")
    
    # Analysis is done on the *filtered_data*
    year_counts = filtered_data["year"].value_counts().sort_index()

    # Create the plot
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    year_counts.plot(kind="bar", ax=ax1, color="skyblue")
    ax1.set_title("Number of Publications per Year")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Number of Papers")
    plt.tight_layout()
    
    # Display in Streamlit
    st.pyplot(fig1)

with col2:
    # --- 2. Horizontal bar chart - top journals ---
    st.subheader(f"Top {top_n_journals} Journals")
    
    # Analysis is done on the *filtered_data*
    top_journals = filtered_data["journal"].value_counts().head(top_n_journals)

    # Create the plot
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    top_journals.sort_values().plot(kind="barh", ax=ax2, color="teal")
    ax2.set_title(f"Top {top_n_journals} Journals Publishing COVID-19 Papers")
    ax2.set_xlabel("Number of Papers")
    ax2.set_ylabel("Journal")
    plt.tight_layout()
    
    # Display in Streamlit
    st.pyplot(fig2)


# --- STEP 5: WORD FREQUENCY (on filtered data) ---
st.header("Content Analysis")
st.subheader(f"Top {top_n_words} Words in Titles")
st.write("(Excluding common words like 'covid', '19', 'study', etc.)")

# Combine all titles from the *filtered* data
all_titles = " ".join(filtered_data["title"].astype(str).str.lower())

# Remove punctuation and split into words
words = re.findall(r'\b\w+\b', all_titles)

# Define a small list of common words to ignore
stop_words = {"the", "and", "of", "in", "a", "to", "on", "for", 
              "with", "an", "by", "at", "from", "about", "study", 
              "covid", "19", "coronavirus", "analysis", "research",
              "sars", "cov", "2", "patient", "patients"} # Added a few more

# Filter words
filtered_words = [w for w in words if w not in stop_words and len(w) > 2]

# Count top N most frequent words
top_words_list = Counter(filtered_words).most_common(top_n_words)

# Display as a clean table
if top_words_list:
    top_words_df = pd.DataFrame(top_words_list, columns=["Word", "Frequency"])
    st.dataframe(top_words_df, use_container_width=True)
else:
    st.write("No titles found to analyze in the selected range.")


# --- STEP 7: SHOW SAMPLE & SAVE CLEANED DATA ---
st.header("Browse Filtered Data")
st.write(f"Showing a sample of 20 articles from the selected period.")

# Show a sample of the *filtered* data
st.dataframe(filtered_data[['publish_date', 'title', 'journal', 'abstract']].head(20))

# Utility function to convert df to csv for download
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(filtered_data)

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name=f"cleaned_metadata_{year_range[0]}_{year_range[1]}.csv",
    mime="text/csv",
)