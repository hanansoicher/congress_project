import time
import pandas as pd
import requests
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import joblib
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from gensim import corpora, models
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from requests.exceptions import RequestException
nltk.download('vader_lexicon', quiet=True)

API_KEY = 'Gej1jav3dg99KkJbAqneBc40kxt7pbeyODF9r1Tt'
BASE_URL = 'https://api.congress.gov/v3'
GICS_FILE_PATH = './data/gics-map-2018.csv'
REPORTS_CSV_FILE_PATH = './data/committee_reports_115-118.csv'
NUM_REPORTS_TO_PROCESS = 100  # Specify the number of reports to process

RATE_LIMIT_CODE = 429
RATE_LIMIT_WAIT = 3600  # Wait 1 hour (3600 seconds)

def fetch_report_text(congress, reportType, reportNumber):
    url = f"{BASE_URL}/committee-report/{congress}/{reportType}/{reportNumber}/text?api_key={API_KEY}"
    while True:
        response = requests.get(url)
        if response.status_code == RATE_LIMIT_CODE:
            print("Rate limit exceeded. Waiting for 1 hour...")
            time.sleep(RATE_LIMIT_WAIT)  # Wait for 1 hour
        elif response.status_code == 200:
            report_data = response.json()
            text_formats = report_data['text'][0]['formats']
            formatted_text_url = next((f['url'] for f in text_formats if f['type'] == 'Formatted Text'), None)
            if formatted_text_url:
                formatted_text_response = requests.get(formatted_text_url)
                if formatted_text_response.status_code == 200:
                    return formatted_text_response.text
                else:
                    print(f"Failed to fetch formatted text: {formatted_text_response.status_code}")
                    return ""
            else:
                print("Formatted Text format not found.")
                return ""
        else:
            print(f"Failed to fetch report text: {response.status_code}")
            return ""

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

def apply_nlp(report_texts):
    sia = SentimentIntensityAnalyzer()
    sentiments = [sia.polarity_scores(text)['compound'] for text in report_texts]
    dictionary = corpora.Dictionary([text.split() for text in report_texts])
    corpus = [dictionary.doc2bow(text.split()) for text in report_texts]
    lda_model = models.LdaModel(corpus, num_topics=10, id2word=dictionary, passes=15)
    topics = [lda_model.get_document_topics(dictionary.doc2bow(text.split())) for text in report_texts]
    return sentiments, topics

SIMILARITY_THRESHOLD = 0.75
vectorizer = joblib.load('./fitted_tfidf_vectorizer.joblib')

def classify_reports(reports_df, gics_df, vectorizer):
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

    reports_df.to_csv(f'./generated_data/classified_reports.csv', index=False)
    return reports_df

def main():
    reports_df = pd.read_csv(REPORTS_CSV_FILE_PATH)
    reports_df['Report Text'] = reports_df['Report Number'].apply(
        lambda report_number: fetch_report_text(
            report_number.split()[-1].split('-')[0], 
            'hrpt' if report_number.startswith('H.') else 
            'srpt' if report_number.startswith('S.') else 
            'erpt' if report_number.startswith('E.') else 
            'unknown', 
            report_number.split()[-1].split('-')[-1])
    )
    sentiments, topics = apply_nlp(reports_df['Report Text'].tolist())
    reports_df['Sentiment'] = sentiments
    reports_df['Topics'] = topics

    gics_df = pd.read_csv(GICS_FILE_PATH)
    classified_reports = classify_reports(reports_df, gics_df, vectorizer)

    classified_reports.to_csv('./generated_data/classified_reports.csv', index=False)

if __name__ == "__main__":
    main()