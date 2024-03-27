import re
from transformers import BertTokenizer, BertModel
import torch
import pandas as pd
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def expand_descriptions(description):
    expanded_desc = [description]
    for word in description.split():
        for syn in wn.synsets(word):
            for lemma in syn.lemmas():
                expanded_desc.append(lemma.name().replace('_', ' '))
    return ' '.join(set(expanded_desc))

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)
    tokens = nltk.word_tokenize(text)
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def get_bert_embeddings(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().detach().numpy()

gics_df = pd.read_csv('./data/gics-map-2018.csv')

gics_df['PreprocessedDescription'] = gics_df['SubIndustryDescription'].apply(preprocess_text).apply(expand_descriptions)

gics_df['BERT_Embeddings'] = gics_df['PreprocessedDescription'].apply(get_bert_embeddings)

gics_df_output = pd.DataFrame()
gics_df_output['SubIndustry'] = gics_df['SubIndustry']
gics_df_output['BERT_Embeddings'] = gics_df['BERT_Embeddings'].apply(lambda x: x.tolist())
gics_df_output['PreprocessedDescription'] = gics_df['PreprocessedDescription']

gics_df_output.to_csv('gics-descriptions-embeddings.csv', index=False)
