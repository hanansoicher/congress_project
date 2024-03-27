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

# Load reports from the database
conn = sqlite3.connect('politics_db.sqlite')
reports_df = pd.read_sql_query('SELECT report_text, ReportNumber, Title FROM committee_reports', conn)
conn.close()

# Preprocessing function
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)
    tokens = nltk.word_tokenize(text)
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

# Apply preprocessing to report texts
reports_df['report_text'] = reports_df['report_text'].apply(preprocess_text)

# Preprocess and vectorize the report texts and expanded descriptions
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

# Calculate the cosine similarity between report vectors and GICS vectors
similarity_scores = cosine_similarity(report_vectors, gics_vectors)

# Classify each report into the top 5 industries with their similarity scores
classified_reports = []
for i, scores in enumerate(similarity_scores):
    top_indices = scores.argsort()[-5:][::-1]  # Get indices of top 5 scores
    top_industries = [(gics_df['SubIndustry'][index], scores[index]) for index in top_indices]
    classified_reports.append((reports_df['Title'][i], top_industries))

# Convert the classification results to a DataFrame
classified_reports_df = pd.DataFrame(classified_reports, columns=['ReportNumber', 'ReportTitle', 'Top5ClassifiedSubIndustries'])

# Create a new SQLite database to store the classifications
classification_conn = sqlite3.connect('classification_db.sqlite')


classified_reports_df['Top5ClassifiedSubIndustries'] = classified_reports_df['Top5ClassifiedSubIndustries'].apply(lambda x: [(industry, float(score)) for industry, score in x]).apply(json.dumps)
classified_reports_df.to_sql('classified_reports', classification_conn, if_exists='replace', index=False)

# Close the connection
classification_conn.close()

print("Classifications saved to the SQLite database successfully.")


