import joblib
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys


ALPHA_VANTAGE_API_KEY = 'FU88M9Q7H9DHFPOM'
ALPHA_VANTAGE_URL = 'https://www.alphavantage.co/query'
REPORTS_CSV_FILE_PATH = './generated_data/classified_reports.csv'
GICS_FILE_PATH = './data/gics-map-2018.csv'  # Adjust the path to your GICS data CSV

def get_asset_industry(asset_symbol):
    params = {
        'function': 'OVERVIEW',
        'symbol': asset_symbol,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(ALPHA_VANTAGE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        industry = data.get('Industry')
        return industry
    else:
        print("Failed to fetch asset data:", response.status_code)
        return None

def find_closest_gics_subindustry(asset_industry, gics_df, vectorizer):
    asset_industry_vec = vectorizer.transform([asset_industry])
    gics_desc_vec = vectorizer.transform(gics_df['SubIndustryDescription'])
    
    similarity_scores = cosine_similarity(asset_industry_vec, gics_desc_vec).flatten()
    highest_score_index = similarity_scores.argmax()
    closest_subindustry = gics_df.iloc[highest_score_index]['SubIndustry']
    
    return closest_subindustry

def find_relevant_reports(closest_subindustry, reports_csv_file_path):
    reports_df = pd.read_csv(reports_csv_file_path)
    relevant_reports = reports_df[reports_df['Closest GICS SubIndustry'].str.contains(closest_subindustry, na=False)]
    return relevant_reports

def main(ticker_symbol):
    industry = get_asset_industry(ticker_symbol)
    if industry:
        gics_df = pd.read_csv(GICS_FILE_PATH)
        vectorizer = joblib.load('./fitted_gics_vectorizer.joblib')
        closest_subindustry = find_closest_gics_subindustry(industry, gics_df, vectorizer)
        relevant_reports = find_relevant_reports(closest_subindustry, REPORTS_CSV_FILE_PATH)
        print(relevant_reports.to_json())  # Output the data as JSON
    else:
        print("No industry information found for the asset.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("No ticker symbol provided.")
