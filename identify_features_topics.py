import sqlite3
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import nltk
from nltk.corpus import stopwords
import re

# Connect to the SQLite database
conn = sqlite3.connect('politics_db.sqlite')

# Select a report by its title
report_title = "21ST CENTURY FLOOD REFORM ACT"
query = "SELECT report_text FROM committee_reports WHERE Title = ?"
report_text = conn.execute(query, (report_title,)).fetchone()[0]

# Load the blacklist of common words
blacklist = []
with open('blacklist.txt', 'r') as file:
    blacklist = file.read().splitlines()

# Preprocess the text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)
    tokens = nltk.word_tokenize(text)
    tokens = [word for word in tokens if word not in stopwords.words('english') and word not in blacklist]
    return ' '.join(tokens)

preprocessed_text = preprocess_text(report_text)

# Feature analysis using TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform([preprocessed_text])
feature_names = vectorizer.get_feature_names_out()
tfidf_scores = tfidf_matrix.toarray().flatten()
top_features = sorted(zip(feature_names, tfidf_scores), key=lambda x: x[1], reverse=True)[:10]
print("Top 10 features by TF-IDF score:")
print(top_features)

# Topic modeling using LDA
lda = LatentDirichletAllocation(n_components=5, random_state=42)
lda.fit(tfidf_matrix)
topic_word_distributions = lda.components_ / lda.components_.sum(axis=1)[:, np.newaxis]
topics = []
for topic_idx, topic in enumerate(topic_word_distributions):
    top_words = [feature_names[i] for i in topic.argsort()[:-11:-1]]
    topics.append((f"Topic {topic_idx+1}", top_words))
print("\nTopics with top 10 words:")
print(topics)
