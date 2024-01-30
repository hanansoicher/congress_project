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
RATE_LIMIT_WAIT = 3600 

def fetch_reports_from_db():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG) # type: ignore
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM committee_reports")
        reports = cursor.fetchall()
        cursor.close()
        conn.close()
        return reports
    except Exception as e:
        print(f"Database error: {e}")
        return []

def fetch_report_text(congress, reportType, reportNumber):
    url = f"{BASE_URL}/committee-report/{congress}/{reportType}/{reportNumber}/text?api_key={API_KEY}"
    while True:
        response = requests.get(url)
        if response.status_code == RATE_LIMIT_CODE:
            print("Rate limit exceeded. Waiting for 1 hour...")
            time.sleep(RATE_LIMIT_WAIT)
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
    nlp = spacy.load('en_core_web_sm')
    sia = SentimentIntensityAnalyzer()
    sentiments = []
    entities = []
    dependencies = []
    dictionary = corpora.Dictionary([text.split() for text in report_texts])
    corpus = [dictionary.doc2bow(text.split()) for text in report_texts]
    lda_model = models.LdaModel(corpus, num_topics=10, id2word=dictionary, passes=15)
    topics = []

    for text in report_texts:
        # Sentiment Analysis
        sentiment = sia.polarity_scores(text)
        sentiments.append(sentiment)

        # NER and Dependency Parsing
        doc = nlp(text)
        entities.append([(ent.text, ent.label_) for ent in doc.ents])
        dependencies.append([(token.text, token.dep_, token.head.text) for token in doc])

        # Topic Modeling
        topics.append(lda_model.get_document_topics(dictionary.doc2bow(text.split())))

    return sentiments, topics, entities, dependencies

vectorizer = joblib.load('./fitted_tfidf_vectorizer.joblib')


def classify_reports(reports_df, gics_df, vectorizer):
    print(f"Number of reports fetched: {len(reports_df)}")
    # Create embeddings for GICS descriptions
    gics_embeddings = vectorizer.transform(gics_df['SubIndustryDescription']).toarray()
    classifications = []

    for index, row in reports_df.iterrows():
        print(f"Processing report {index + 1}/{len(reports_df)}")
        report_text = fetch_report_text(row['congress'], row['type'], row['number'])
        processed_text = preprocess_text(report_text)
        print(f"Report processed. Length of processed text: {len(processed_text)} characters")

        # Create embeddings for the report text
        report_embedding = vectorizer.transform([processed_text]).toarray()

        similarity_scores = cosine_similarity(report_embedding, gics_embeddings).flatten()
        matched_gics = gics_df.iloc[similarity_scores >= 0.75]['SubIndustry'].tolist()

        classifications.append((matched_gics, similarity_scores.tolist()))

    return classifications

def insert_classifications_into_db(report_id, classifications):
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG) # type: ignore
        cur = conn.cursor()

        for closest_gics_subindustry, similarity_scores in classifications:
            similarity_scores_str = ','.join(map(str, similarity_scores))

            cur.execute("INSERT INTO ReportClassifications (ReportID, ClosestGICSSubIndustry, SimilarityScores) VALUES (%s, %s, %s)",
                        (report_id, closest_gics_subindustry, similarity_scores_str))

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"An error occurred while inserting classification into the database: {e}")

def insert_nlp_results_into_db(nlp_results):
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG) # type: ignore
        cur = conn.cursor()

        # Insert data
        for result in nlp_results:
            report_id, sentiment, topics, entities, dependencies = result

            # Insert into SentimentAnalysis table
            cur.execute("INSERT INTO SentimentAnalysis (ReportID, Negative, Neutral, Positive, Compound) VALUES (%s, %s, %s, %s, %s)",
                        (report_id, sentiment['neg'], sentiment['neu'], sentiment['pos'], sentiment['compound']))

            # Insert into Topics table
            for topic in topics:
                topic_id, contribution = topic
                cur.execute("INSERT INTO Topics (ReportID, TopicID, Contribution) VALUES (%s, %s, %s)",
                            (report_id, topic_id, contribution))

            # Insert into NamedEntities table
            for entity in entities:
                entity_text, entity_type = entity
                cur.execute("INSERT INTO NamedEntities (ReportID, Entity, EntityType) VALUES (%s, %s, %s)",
                            (report_id, entity_text, entity_type))

            # Insert into Dependencies table
            for dependency in dependencies:
                word, dep, head = dependency
                cur.execute("INSERT INTO Dependencies (ReportID, Word, Dependency, Head) VALUES (%s, %s, %s, %s)",
                            (report_id, word, dep, head))

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"An error occurred while inserting into the database: {e}")

def main():
    reports = fetch_reports_from_db()
    reports_df = pd.DataFrame(reports, columns=['report_id', 'congress', 'chamber', 'is_conference_report', 'issue_date', 'report_number', 'part', 'session_number', 'text_url', 'title', 'report_type', 'update_date'])
    nlp_results = []
    gics_df = pd.read_csv(GICS_FILE_PATH)

    for _, report in reports_df.iterrows():
        print(report)
        report_text = preprocess_text(fetch_report_text(report['congress'], report['report_type'], report['report_number']))
        sentiments, topics, entities, dependencies = apply_nlp([report_text])
        nlp_result = (report['report_id'], sentiments[0], topics[0], entities[0], dependencies[0])
        nlp_results.append(nlp_result)

        classifications = classify_reports(report, gics_df, vectorizer)
        insert_classifications_into_db(report['report_id'], classifications)

    insert_nlp_results_into_db(nlp_results)

if __name__ == "__main__":
    main()