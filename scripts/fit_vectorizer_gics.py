import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


GICS_FILE_PATH = './data/gics-map-2018.csv'
gics_df = pd.read_csv(GICS_FILE_PATH)
vectorizer = TfidfVectorizer()
vectorizer.fit(gics_df['SubIndustryDescription'])
joblib.dump(vectorizer, 'gics_vectorizer.joblib')
