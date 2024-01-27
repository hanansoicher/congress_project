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


API_KEY = 'Gej1jav3dg99KkJbAqneBc40kxt7pbeyODF9r1Tt'
BASE_URL = 'https://api.congress.gov/v3'

def get_reports_by_congress(congress, limit=250):
    url = f"{BASE_URL}/committee-report/{congress}?api_key={API_KEY}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Reports successfully fetched for Congress {congress}.")
        return pd.DataFrame(response.json()['reports'])
    else:
        print(f"Failed to fetch reports for Congress {congress}: {response.status_code}")
        return pd.DataFrame()

def fetch_all_reports(start_congress=113):
    all_reports = pd.DataFrame()
    for congress in range(start_congress, 119): 
        reports = get_reports_by_congress(congress)
        all_reports = pd.concat([all_reports, reports], ignore_index=True)
    return all_reports

# Fetch reports for all Congresses from 113th to 117th
reports_df = fetch_all_reports()

    
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
            print(f"Fetching report text from URL: {text_url}")
            if text_url.endswith('.pdf'):
                response = requests.get(text_url, stream=True)
                response.raise_for_status()
                with io.BytesIO(response.content) as pdf_file:
                    with pdfplumber.open(pdf_file) as pdf:
                        return ''.join([page.extract_text() for page in pdf.pages])
            else:
                return requests.get(text_url).text
        else:
            print("No suitable format found.")
            return ""
    else:
        print(f"Failed to fetch report text: {response.status_code}")
        return ""

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # Tokenize
    tokens = word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    return ' '.join(tokens)

# Fetch a large set of reports
reports_df = fetch_all_reports()

# Preprocess all report texts
processed_texts = [preprocess_text(fetch_report_text(row['congress'], row['type'], row['number'])) for _, row in reports_df.iterrows()]

# Initialize and fit the TF-IDF vectorizer
vectorizer = TfidfVectorizer()
vectorizer.fit(processed_texts)

joblib.dump(vectorizer, 'fitted_tfidf_vectorizer.joblib')
