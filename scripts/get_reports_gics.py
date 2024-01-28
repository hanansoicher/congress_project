import requests
import pandas as pd
import io
import PyPDF2
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
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
            print(f"Fetching report text from URL: {text_url}")
            if text_url.endswith('.pdf'):
                with requests.get(text_url, stream=True) as r:
                    r.raise_for_status()
                    with io.BytesIO() as pdf_file:
                        for chunk in r.iter_content(chunk_size=8192):
                            pdf_file.write(chunk)
                        pdf_file.seek(0)                
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        return ''.join([page.extract_text() for page in pdf_reader.pages])
            else:
                return requests.get(text_url).text
        else:
            print("No suitable format found.")
            return ""
    else:
        print(f"Failed to fetch report text: {response.status_code}")
        return ""

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def encode_gics_descriptions(gics_df):
    model.eval() # type: ignore
    encoded_texts = tokenizer.batch_encode_plus(gics_df['SubIndustryDescription'].tolist(), 
                                                padding=True, 
                                                truncation=True, 
                                                return_tensors='pt')
    with torch.no_grad():
        outputs = model(**encoded_texts) # type: ignore
    return outputs.pooler_output

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

SIMILARITY_THRESHOLD = 0.75
vectorizer = joblib.load('./fitted_tfidf_vectorizer.joblib')

def classify_reports(congress, gics_df, vectorizer):
    reports_df = get_reports_by_congress(congress)
    print(f"Number of reports fetched: {len(reports_df)}")
    
    # Create embeddings for GICS descriptions
    gics_embeddings = vectorizer.transform(gics_df['SubIndustryDescription']).toarray()

    # Iterate through each report
    for index, row in reports_df.iterrows():
        print(f"Processing report {index + 1}/{len(reports_df)}") # type: ignore
        report_text = fetch_report_text(row['congress'], row['type'], row['number'])
        processed_text = preprocess_text(report_text)
        print(f"Report processed. Length of processed text: {len(processed_text)} characters")

        # Create embeddings for the report text
        report_embedding = vectorizer.transform([processed_text]).toarray()

        # Compute cosine similarity with GICS embeddings
        similarity_scores = cosine_similarity(report_embedding, gics_embeddings).flatten()

        # Find all GICS classifications that exceed the similarity threshold
        matching_indices = similarity_scores >= SIMILARITY_THRESHOLD
        matches = gics_df.iloc[matching_indices]['SubIndustryDescription'].tolist()

        if not matches:
            # No match above threshold, take the highest scoring one
            highest_score_index = similarity_scores.argmax()
            matches = [gics_df.iloc[highest_score_index]['SubIndustryDescription']]

        # Store the results in the DataFrame
        reports_df.at[index, 'Closest GICS'] = ', '.join(matches)
        print(f"Closest GICS: {', '.join(matches)}")

    # Save the DataFrame
    reports_df.to_csv(f'./generated_data/classified_reports_{congress}.csv', index=False)
    return reports_df

# Load the pre-fitted TF-IDF vectorizer
vectorizer = joblib.load('fitted_tfidf_vectorizer.joblib')

# Example usage
gics_df = pd.read_csv('./data/gics-map-2018.csv')
classified_reports = classify_reports(117, gics_df, vectorizer)
