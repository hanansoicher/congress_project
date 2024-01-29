import io
import re
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import pdfplumber
import joblib
import random

API_KEY = 'Gej1jav3dg99KkJbAqneBc40kxt7pbeyODF9r1Tt'
BASE_URL = 'https://api.congress.gov/v3'

def get_random_reports(file_path, num_reports):
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Data loaded successfully. Sampling {num_reports} random reports...")
    random_reports = df.sample(n=num_reports, random_state=1)
    return random_reports

def fetch_report_text(congress, reportType, reportNumber):
    url = f"{BASE_URL}/committee-report/{congress}/{reportType}/{reportNumber}/text?api_key={API_KEY}"
    print(f"Fetching report metadata from API URL: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()

        report_data = response.json()
        text_formats = report_data['text']

        formatted_text_url = None
        for text_format in text_formats:
            format_entry = text_format['formats'][0]
            if format_entry['type'] == 'Formatted Text':
                formatted_text_url = format_entry['url']
                break

        if formatted_text_url:
            print(f"Fetching formatted text from .htm URL: {formatted_text_url}")
            formatted_text_response = requests.get(formatted_text_url)
            if formatted_text_response.status_code == 200:
                fetched_text = formatted_text_response.text
                print(f"Formatted text fetched successfully. Length of text: {len(fetched_text)} characters.")
                return fetched_text
            else:
                print(f"Failed to fetch formatted text: {formatted_text_response.status_code}")
                return ""

        print("Formatted Text format not found.")
        return ""

    except requests.RequestException as e:
        print(f"Failed to fetch report text due to an error: {e}")
        return ""

    
def preprocess_text(text):
    print("Preprocessing text...")
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

random_reports = get_random_reports('./data/committee_reports_115-118.csv', 1000)
print(f"Columns in the sampled reports: {random_reports.columns}")
processed_texts = [preprocess_text(fetch_report_text(row['Report Number'].split()[-1].split('-')[0], 'hrpt' if row['Report Number'].startswith('H') else 'srpt' if row['Report Number'].startswith('S') else 'erpt' if row['Report Number'].startswith('E') else 'unknown', row['Report Number'].split()[-1].split('-')[-1])) for _, row in random_reports.iterrows()]

print("Fitting TF-IDF Vectorizer...")
vectorizer = TfidfVectorizer()
vectorizer.fit(processed_texts)
print("Vectorizer fitted successfully.")

joblib.dump(vectorizer, 'fitted_tfidf_vectorizer.joblib')
print("Vectorizer saved to 'fitted_tfidf_vectorizer.joblib'.")
