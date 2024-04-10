import sqlite3
import pandas as pd
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords

conn = sqlite3.connect('./data/politics_db.sqlite')
reports_df = pd.read_sql_query('SELECT report_text FROM committee_reports LIMIT 500', conn).dropna()
conn.close()

def preprocess_text(text):
    if text:
        text = text.lower()
        text = re.sub(r'\W', ' ', text)
        tokens = nltk.word_tokenize(text)
        tokens = [word for word in tokens if word not in stopwords.words('english')]
        return ' '.join(tokens)

reports_df['preprocessed_text'] = reports_df['report_text'].apply(preprocess_text)

word_report_indices = {}

for idx, text in enumerate(reports_df['preprocessed_text']):
    words = set(text.split())
    for word in words:
        if word in word_report_indices:
            word_report_indices[word].add(idx)
        else:
            word_report_indices[word] = {idx}

report_count = len(reports_df)
word_report_portion = {word: len(indices) / report_count for word, indices in word_report_indices.items()}

blacklist_threshold = 0.6
blacklist = [word for word, portion in word_report_portion.items() if portion > blacklist_threshold]

with open('data/blacklist.txt', 'w') as f:
    for word in blacklist:
        f.write(f"{word}\n")
