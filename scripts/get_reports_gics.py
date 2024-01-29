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
from requests.exceptions import RequestException

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

def get_committee_reports(from_date, to_date):
    url = f"{BASE_URL}/committee-report?api_key={API_KEY}&fromDateTime={from_date}T00:00:00Z&toDateTime={to_date}T00:00:00Z&limit=20"
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json()['reports'])
    else:
        print(f"Failed to fetch reports: {response.status_code}")
        return pd.DataFrame()

def fetch_report_text(congress, reportType, reportNumber):
    url = f"{BASE_URL}/committee-report/{congress}/{reportType}/{reportNumber}/text?api_key={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()

        report_data = response.json()
        text_formats = report_data['text'][0]['formats']

        formatted_text_url = next((f['url'] for f in text_formats if f['type'] == 'Formatted Text'), None)
        if formatted_text_url:
            formatted_text_response = requests.get(formatted_text_url)
            if formatted_text_response.status_code == 200:
                return formatted_text_response.text
            else:
                print(f"Failed to fetch formatted text: {formatted_text_response.status_code}")
        else:
            print("Formatted Text format not found.")

        print("Skipping PDF processing.")
        return ""

    except requests.RequestException as e:
        print(f"Failed to fetch report text: {e}")
        return ""


def fetch_report_text_limit_pdfs(congress, reportType, reportNumber, max_size=10*1024*1024):  # 10 MB size limit
    url = f"{BASE_URL}/committee-report/{congress}/{reportType}/{reportNumber}/text?api_key={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()

        report_data = response.json()
        text_formats = report_data['text'][0]['formats']

        # First, check for 'Formatted Text' type and process it
        formatted_text_url = next((f['url'] for f in text_formats if f['type'] == 'Formatted Text'), None)
        if formatted_text_url:
            return requests.get(formatted_text_url).text

        for format in text_formats:
            if format['type'] == 'PDF':
                pdf_url = format['url']
                head_response = requests.head(pdf_url)
                content_length = int(head_response.headers.get('Content-Length', 0))
                print(content_length)
                if content_length > max_size:
                    print(f"PDF is too large to process: {content_length} bytes.")
                    continue  
                
                pdf_response = requests.get(pdf_url, stream=True)
                pdf_response.raise_for_status()
                with io.BytesIO(pdf_response.content) as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    text = ''.join([page.extract_text() for page in pdf_reader.pages])
                    return text

        print("No suitable format found.")
        return ""

    except RequestException as e:
        print(f"Failed to fetch report text: {e}")
    
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
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = word_tokenize(text)

    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

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
    similarity_scores_list = []

    for index, row in reports_df.iterrows():
        print(f"Processing report {index + 1}/{len(reports_df)} from url: {row['url']}") # type: ignore
        report_text = fetch_report_text(row['congress'], row['type'], row['number'])
        processed_text = preprocess_text(report_text)
        print(f"Report processed. Length of processed text: {len(processed_text)} characters")

        # Create embeddings for the report text
        report_embedding = vectorizer.transform([processed_text]).toarray()

        similarity_scores = cosine_similarity(report_embedding, gics_embeddings).flatten()
        similarity_scores_list.append(similarity_scores) 

        matching_indices = similarity_scores >= SIMILARITY_THRESHOLD
        if any(matching_indices):
            matched_gics = gics_df.iloc[matching_indices][['SubIndustry']]
            matched_subindustries = matched_gics['SubIndustry'].tolist()
        else:
            highest_score_index = similarity_scores.argmax()
            matched_subindustries = [gics_df.iloc[highest_score_index]['SubIndustry']]

        reports_df.at[index, 'Closest GICS SubIndustry'] = ', '.join(matched_subindustries)
        print(f"Closest GICS SubIndustry: {', '.join(matched_subindustries)}")

    reports_df['Similarity Scores'] = similarity_scores_list

    reports_df.to_csv(f'./generated_data/classified_reports_{congress}.csv', index=False)
    return reports_df

# Load the pre-fitted TF-IDF vectorizer
vectorizer = joblib.load('fitted_tfidf_vectorizer.joblib')

# Example usage
gics_df = pd.read_csv('./data/gics-map-2018.csv')
classified_reports = classify_reports(117, gics_df, vectorizer)
