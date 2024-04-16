# To Run: streamlit run Book_rec_app.py --server.port=8888

import nltk
import streamlit as st
import pickle
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity

#%%
st.set_page_config(
    page_title="AI Book Recommendation",
    page_icon=":books:",
)

#%%
st.title('AI Book Recommendation App')
with st.expander(":open_book: Welcome to AI Book Recommendation!", expanded=False):
    st.write(
        """     
    - Provide a short book review and receive tailored recommendations for your next read.
    - Use the intuitive controls on the left to tailor your experience to your preferences.
        """
    )

# Step-by-Step Guide
with st.expander(":open_book: How to Use", expanded=False):
    st.write(
        """
    1. **Enter Book Review:**
        - Type or paste a 3-5 sentence review of a book you enjoyed to find more like it.
        - Hint: Tell us what you liked most about a recent read.
        - Be descriptive, get creative! :stuck_out_tongue_winking_eye:

    2. **Choose Features:**
        - Toggle the switch on the left sidebar to choose between SVD and Transformers4Rec models.
        - Which model gives you better results?
        """
    )

#%%#
# SVD Model code

@st.cache_resource()
# Lazy load the model and data
def lazy_load_model_and_data():
    with open('/home/ubuntu/caitlin/NLP_Project_Team1/data/SVD_recommendations_17.pkl', 'rb') as f:
        lsa_model = pickle.load(f)
    with open('/home/ubuntu/caitlin/NLP_Project_Team1/data/X_matrix_17.pkl', 'rb') as f:
        X = pickle.load(f)
    data = pd.read_parquet('/home/ubuntu/caitlin/NLP_Project_Team1/data/books_merged_clean.parquet')
    return lsa_model, X, data


# Function to preprocess the text
def preprocess_text(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove special characters and punctuation
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Remove extra whitespaces
    text = " ".join(text.split())
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = nltk.word_tokenize(text)
    text = " ".join([word for word in tokens if word not in stop_words])
    # Perform lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = nltk.word_tokenize(text)
    text = " ".join([lemmatizer.lemmatize(word) for word in tokens])
    return text

# Function to clean Book title
def clean_title(title):
    # Lowercase all characters
    title = title.lower()
    # Remove comma and semicolon
    title = title.replace(',', '').replace(';', '')
    # Capitalize first word only
    title = title.capitalize()
    return title

# Function to generate recommendations
def get_svd_recommendations(text_input):
    # Lazy load model and data
    lsa_model, X, data = lazy_load_model_and_data()
    # Preprocess the text
    processed_text = preprocess_text(text_input)
    # Transform the preprocessed text input
    input_vector = lsa_model.transform([processed_text])
    # Compute cosine similarity between input vector and all book vectors
    similarities = cosine_similarity(input_vector, X)
    # Get indices of top recommendations
    top_indices = similarities.argsort()[0][::-1][:35]  # Get top 35 recommendations
    # Retrieve recommended books
    recommendations = data.iloc[top_indices]
    # Apply clean_title function to the 'Title' column
    recommendations = recommendations.copy() # ensure that any modifications are made to a separate copy
    recommendations.loc[:, 'Title'] = recommendations['Title'].apply(clean_title)
    # Remove duplicates based on review summary
    recommendations = recommendations.drop_duplicates(subset=['review/summary'], keep='first')
    # Sort recommendations by rating (review/score)
    recommendations = recommendations.sort_values(by='review/score', ascending=False)
    # Return top non-duplicate recommendations
    return recommendations[['Title', 'categories', 'review/summary', 'review/text', 'previewLink']].head(10)

#%%
# Main function to run the Streamlit app
def main():
    st.title('Your next story starts here...')

    # Sidebar to select model type
    model_type = st.sidebar.radio("Select Model Type", ("SVD", "Transformers4Rec"))

    # Text input area for book review
    input_text = st.text_area("Enter your book review (3-5 sentences):")

    if st.button("Get Recommendations"):
        if model_type == "SVD":
            recommendations = get_svd_recommendations(input_text)
            # st.write("SVD recommendations coming soon!")
            st.write("**Recommendations:**")
            st.dataframe(recommendations, hide_index=True)
        elif model_type == "Transformers4Rec":
            # recommendations = get_transformer4rec_recommendations(input_text, data)
            st.write("Transformers4Rec recommendations coming soon!")


        # Output recommendations
        # st.write("**Recommendations:**")
        # st.table(recommendations)


if __name__ == "__main__":
    main()