import pandas as pd
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel
import torch
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import ast
import json

conn = sqlite3.connect('./data/reports_db.sqlite')
query = """
SELECT cr.report_text, cr.ReportNumber, cr.Title
FROM committee_reports cr
LEFT JOIN report_classifications rc ON cr.ReportNumber = rc.ReportNumber
WHERE rc.ReportNumber IS NULL
"""

reports_df = pd.read_sql_query(query, conn)

# reports_df = pd.read_sql_query('SELECT report_text, ReportNumber, Title FROM committee_reports LIMIT 100', conn)

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)
    tokens = nltk.word_tokenize(text)
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

reports_df['report_text'] = reports_df['report_text'].apply(preprocess_text)

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def bert_vectorize(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().detach().numpy()

report_vectors = torch.stack([torch.tensor(bert_vectorize(text)) for text in reports_df['report_text']])

gics_df = pd.read_csv('./data/gics-descriptions-embeddings.csv')
gics_df['BERT_Embeddings'] = gics_df['BERT_Embeddings'].apply(ast.literal_eval)
gics_vectors = torch.stack([torch.tensor(embedding) for embedding in gics_df['BERT_Embeddings']])

similarity_scores = cosine_similarity(report_vectors, gics_vectors)

similarity_threshold = 0.75

classified_reports = []
for i, scores in enumerate(similarity_scores):
    above_threshold_indices = [index for index, score in enumerate(scores) if score > similarity_threshold]
    above_threshold_industries = [(gics_df['SubIndustry'][index], scores[index]) for index in above_threshold_indices]
    classified_reports.append((reports_df['ReportNumber'][i], reports_df['Title'][i], above_threshold_industries))

classified_reports_df = pd.DataFrame(classified_reports, columns=['ReportNumber', 'ReportTitle', 'ClassifiedSubIndustries'])

classified_reports_df['ClassifiedSubIndustries'] = classified_reports_df['ClassifiedSubIndustries'].apply(lambda x: [(industry, float(score)) for industry, score in x]).apply(json.dumps)
classified_reports_df.to_sql('report_classifications', conn, if_exists='replace', index=False)

conn.close()
print("Classifications saved to the reports_db SQLite database successfully.")