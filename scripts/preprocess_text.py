from bs4 import BeautifulSoup
import joblib
import requests
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
import pandas as pd
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import PyPDF2
import io

API_KEY = 'Gej1jav3dg99KkJbAqneBc40kxt7pbeyODF9r1Tt'
BASE_URL = 'https://api.congress.gov/v3'

# Function to get the list of committee reports
def get_committee_reports(from_date, to_date):
    url = f"{BASE_URL}/committee-report?api_key={API_KEY}&fromDateTime={from_date}T00:00:00Z&toDateTime={to_date}T00:00:00Z&limit=20"
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json()['reports'])
    else:
        print(f"Failed to fetch reports: {response.status_code}")
        return pd.DataFrame()

# Function to get specific report text
def fetch_report_text(congress, reportType, reportNumber):
    url = f"{BASE_URL}/committee-report/{congress}/{reportType}/{reportNumber}/text?api_key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        report_data = response.json()
        text_formats = report_data['text'][0]['formats']

        text_url = None
        for format in text_formats:
            if format['type'] == 'Formatted Text':
                text_url = format['url']
                break
            elif format['type'] == 'PDF':
                text_url = format['url']

        if text_url:
            print(text_url)
            if text_url.endswith('.pdf'):
                with requests.get(text_url, stream=True) as r:
                    r.raise_for_status()
                    with io.BytesIO() as pdf_file:
                        for chunk in r.iter_content(chunk_size=8192):
                            print(chunk)
                            pdf_file.write(chunk)
                        pdf_file.seek(0)                
                        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
                        return ''.join([page.extract_text() for page in pdf_reader.pages])
            else:
                return requests.get(text_url).text
        else:
            print("No suitable format found.")
            return ""
    else:
        print(f"Failed to fetch report text: {response.status_code}")
        return ""

def preprocess_text(text):
    """Preprocess the text: tokenization, lowercasing, removing stopwords, and lemmatization."""
    tokens = word_tokenize(text)
    tokens = [token.lower() for token in tokens]
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    print(tokens[:5])
    return tokens

# Displaying topics
def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print(f"Topic {topic_idx}:")
        print(" ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))

# Specify your date range
from_date = '2023-12-01'
to_date = '2023-12-31'

# Get the general list of reports
reports_df = get_committee_reports(from_date, to_date)

def apply_lda_to_single_document(text):
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    transformed_data = vectorizer.fit_transform([text])
    lda_model = LatentDirichletAllocation(n_components=5, random_state=42)
    lda_model.fit(transformed_data)
    return lda_model, vectorizer

# Create a DataFrame to store topics for each report
topics_df = pd.DataFrame()

for index, row in reports_df.iterrows():
    full_text = fetch_report_text(row['congress'], row['type'], row['number'])
    print(full_text)
    processed_text = ' '.join(preprocess_text(full_text))

    # Apply LDA and get topics for each report
    if processed_text.strip():
        lda_model, vectorizer = apply_lda_to_single_document(processed_text)
        topics = [' '.join([str(vectorizer.get_feature_names_out()[i]) for i in topic.argsort()[:-10 - 1:-1]]) for topic in lda_model.components_]
        
        # Append topics and report details to DataFrame
        topics_df = topics_df.append({'Report Number': row['number'], 'Congress': row['congress'], 'Type': row['type'], 'Topics': topics}, ignore_index=True) # type: ignore

# Combine with general reports DataFrame
final_df = pd.merge(reports_df, topics_df, on=['Report Number', 'Congress', 'Type'])

# Save the final DataFrame
final_df.to_csv('final_reports_with_topics.csv', index=False)
