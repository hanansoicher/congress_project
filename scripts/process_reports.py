import json
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
import psycopg2
import psycopg2.extras
from requests.exceptions import RequestException
import spacy
import xml.etree.ElementTree as ET
nltk.download('vader_lexicon', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)

API_KEY = 'Gej1jav3dg99KkJbAqneBc40kxt7pbeyODF9r1Tt'
BASE_URL = 'https://api.congress.gov/v3'
GICS_FILE_PATH = './data/gics-map-2018.csv'
DATABASE_CONFIG = {
    'dbname': 'politics_db',
    'user': 'postgres',
    'password': 'Ignorantbliss(9)',
    'host': 'localhost'
}
RATE_LIMIT_CODE = 429
RATE_LIMIT_WAIT = 1800 
vectorizer = joblib.load('./fitted_tfidf_vectorizer.joblib')

def fetch_reports_from_db():
    print("Fetching reports from the database...")
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG) #type: ignore
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM committee_reports")
        reports = cursor.fetchall()
        cursor.close()
        conn.close()
        print(f"Fetched {len(reports)} reports.")
        return reports
    except Exception as e:
        print(f"Database error: {e}")
        return []

def fetch_report_text(congress, reportType, reportNumber):
    print(f"Fetching report text for Congress {congress}, Type {reportType}, Number {reportNumber}...")
    text_url = fetch_report_text_from_db(congress, reportType, reportNumber)
    if not text_url:
        print("URL not found in database, constructing URL...")
        text_url = f"{BASE_URL}/committee-report/{congress}/{reportType}/{reportNumber}/text?api_key={API_KEY}"
    
    attempt = 0
    while attempt < 3:
        print(f"Attempt {attempt+1}: Fetching report text...")
        response = requests.get(text_url)
        if response.status_code == RATE_LIMIT_CODE:
            print("Rate limit exceeded. Waiting to retry...")
            time.sleep(RATE_LIMIT_WAIT)
            attempt += 1
            continue
        elif response.status_code == 200:
            try:
                data = json.loads(response.text)
                formatted_text_url = None
                for item in data.get('text', []):
                    for format_item in item.get('formats', []):
                        if format_item.get('type') == 'Formatted Text':
                            formatted_text_url = format_item.get('url')
                            break
                    if formatted_text_url:
                        print("Formatted text URL found, fetching content...")
                        return fetch_content_with_rate_limit_handling(formatted_text_url)
                else:
                    print("Formatted Text URL not found in JSON.")
                    return ""
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                return ""
        else:
            print(f"Failed to fetch report text: HTTP {response.status_code}")
            return ""
        break

def fetch_content_with_rate_limit_handling(url):
    print(f"Fetching content from URL with rate limit handling: {url}")
    attempt = 0
    while attempt < 3:
        response = requests.get(url)
        if response.status_code == RATE_LIMIT_CODE:
            print("Rate limit exceeded. Waiting to retry...")
            time.sleep(RATE_LIMIT_WAIT)
            attempt += 1
        elif response.status_code == 200:
            print("Content successfully fetched.")
            return response.text
        else:
            print(f"Failed to fetch content: HTTP {response.status_code}")
            return ""
    return ""

def fetch_report_text_from_db(congress, reportType, reportNumber):
    print(f"Attempting to fetch the report text URL from the database for Congress {congress}, Type {reportType}, Number {reportNumber}...")
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG) #type: ignore
        cursor = conn.cursor()
        cursor.execute("""
            SELECT text_url FROM committee_reports
            WHERE congress = %s AND report_type = %s AND report_number = %s;
        """, (congress, reportType, reportNumber))
        result = cursor.fetchone()
        conn.close()
        if result:
            print("URL found in database.")
        else:
            print("URL not found in database.")
        return result[0] if result else None
    except Exception as e:
        print(f"Database error: {e}")
        return None

def save_report_text_to_db(congress, reportType, reportNumber, text):
    print(f"Saving report text to the database for Congress {congress}, Type {reportType}, Number {reportNumber}...")
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG) #type: ignore
        cur = conn.cursor()
        cur.execute("""
            UPDATE committee_reports
            SET report_text = %s
            WHERE congress = %s AND report_type = %s AND report_number = %s;
        """, (text, congress, reportType, reportNumber))
        conn.commit()
        cur.close()
        conn.close()
        print("Report text saved successfully.")
    except Exception as e:
        print(f"Database error while saving report text: {e}")

def preprocess_text(text):
    print("Preprocessing text...")
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    preprocessed_text = ' '.join(tokens)
    print("Text preprocessing completed.")
    return preprocessed_text

def apply_nlp(text):
    print("Applying NLP to text...")
    nlp = spacy.load('en_core_web_sm')
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    dependencies = [(token.text, token.dep_, token.head.text) for token in doc]
    print("NLP application completed.")
    return sentiment, entities, dependencies

def classify_report(report_text, gics_df, vectorizer):
    print("Classifying report...")
    report_embedding = vectorizer.transform([report_text]).toarray()
    gics_embeddings = vectorizer.transform(gics_df['SubIndustryDescription']).toarray()
    similarity_scores = cosine_similarity(report_embedding, gics_embeddings).flatten()
    matched_gics = gics_df.iloc[similarity_scores >= 0.75]['SubIndustry'].tolist()
    print("Report classification completed.")
    return matched_gics, similarity_scores.tolist()

def insert_classifications_into_db(report_id, classifications):
    print(f"Inserting classifications into the database for report ID {report_id}...")
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG) #type: ignore
        cur = conn.cursor()

        for closest_gics_subindustry, similarity_scores in classifications:
            similarity_scores_str = ','.join(map(str, similarity_scores))

            cur.execute("INSERT INTO ReportClassifications (report_id, closestgicssubIndustry, similarityscores) VALUES (%s, %s, %s)",
                        (report_id, closest_gics_subindustry, similarity_scores_str))

        conn.commit()
        cur.close()
        conn.close()
        print("Classifications inserted successfully.")
    except Exception as e:
        print(f"An error occurred while inserting classification into the database: {e}")

def insert_nlp_results_into_db(nlp_results):
    print("Inserting NLP results into the database...")
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG) #type: ignore
        cur = conn.cursor()

        for result in nlp_results:
            report_id, sentiment, entities, dependencies = result

            cur.execute("INSERT INTO SentimentAnalysis (report_id, negative, neutral, positive, compound) VALUES (%s, %s, %s, %s, %s)",
                        (report_id, sentiment['neg'], sentiment['neu'], sentiment['pos'], sentiment['compound']))

            for entity in entities:
                entity_text, entity_type = entity
                cur.execute("INSERT INTO NamedEntities (report_id, entity, entitytype) VALUES (%s, %s, %s)",
                            (report_id, entity_text, entity_type))

            for dependency in dependencies:
                word, dep, head = dependency
                cur.execute("INSERT INTO Dependencies (report_id, word, dependency, head) VALUES (%s, %s, %s, %s)",
                            (report_id, word, dep, head))

        conn.commit()
        cur.close()
        conn.close()
        print("NLP results inserted successfully.")
    except Exception as e:
        print(f"An error occurred while inserting into the database: {e}")

def process_reports(reports):
    print("Processing reports...")
    dictionary = corpora.Dictionary()
    corpus = []
    nlp_results = []

    for report in reports:
        processed_text = report['report_text']
        tokens = processed_text.split()
        dictionary.add_documents([tokens])
        corpus.append(dictionary.doc2bow(tokens))
    
    lda_model = models.LdaModel(corpus, num_topics=10, id2word=dictionary, passes=15)
    print("LDA model applied.")

    for report in reports:
        sentiment, entities, dependencies = apply_nlp(report['report_text'])
        topics = lda_model.get_document_topics(dictionary.doc2bow(report['report_text'].split(" ")))
        nlp_results.append({
            'report_id': report['report_id'],
            'sentiment': sentiment,
            'entities': entities,
            'dependencies': dependencies,
            'topics': topics
        })

    print("Reports processed.")
    return nlp_results

def main():
    print("Starting main process...")
    reports = fetch_reports_from_db()
    
    for report in reports:
        if not report['report_text']:
            print("Report text not found, fetching from API...")
            text = fetch_report_text(report['congress'], report['report_type'], report['report_number'])
            save_report_text_to_db(report['congress'], report['report_type'], report['report_number'], preprocess_text(text))
    
    reports = fetch_reports_from_db()
    nlp_results = process_reports(reports)
    insert_nlp_results_into_db(nlp_results)

    gics_df = pd.read_csv(GICS_FILE_PATH)
    for report in reports:
        classifications = classify_report(report['report_text'], gics_df, vectorizer)
        insert_classifications_into_db(report['report_id'], classifications)

    print("Main process completed.")

if __name__ == "__main__":
    main()
