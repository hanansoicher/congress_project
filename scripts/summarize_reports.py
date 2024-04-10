import sqlite3
import logging
import argparse
from transformers import pipeline
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and word.isalpha()]
    return ' '.join(tokens)

def chunk_text(text, chunk_size=900):
    tokens = word_tokenize(text)
    logging.info("sentences tokenized")
    chunks = []
    current_chunk = []

    for token in tokens:
        if len(current_chunk) + 10 > chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = [token]
        else:
            current_chunk.append(token)

    if current_chunk:
        chunks.append(' '.join(current_chunk))
    logging.info(f"Number of chunks: {len(chunks)}")
    return chunks


def generate_summary(text, max_length=200, final_summary_length=100):
    preprocessed_text = preprocess_text(text)

    chunks = chunk_text(preprocessed_text, chunk_size=900)
    if len(chunks) < 20:
        
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        chunk_summaries = [summarizer(chunk, max_length=max_length, min_length=25, do_sample=False)[0]['summary_text'] for chunk in chunks]

        combined_summaries = ' '.join(chunk_summaries)

        final_chunks = chunk_text(combined_summaries, chunk_size=900)
        final_summary = [summarizer(chunk, max_length=final_summary_length, min_length=20, do_sample=False)[0]['summary_text'] for chunk in final_chunks]

        return ''.join(final_summary)
    else:
        return "Long report, skipped for now"

def update_report_summaries(db_path, batch_size=20):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        while True:
            cursor.execute("SELECT ReportNumber, report_text FROM committee_reports WHERE summary IS NULL LIMIT ?", (batch_size,))
            reports = cursor.fetchall()
            if not reports:
                break

            for report_number, report_text in reports:
                try:
                    logging.info(f"Generating summary for report {report_number}...")
                    summary = generate_summary(report_text)
                    cursor.execute("UPDATE committee_reports SET summary = ? WHERE ReportNumber = ?", (summary, report_number))
                    conn.commit()
                except Exception as e:
                    logging.error(f"Error generating summary for report {report_number}: {e}")


            logging.info(f"Updated summaries for {len(reports)} reports.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update report summaries in the database.")
    parser.add_argument("--db_path", type=str, default="./data/reports_db.sqlite", help="Path to the SQLite database file.")
    parser.add_argument("--batch_size", type=int, default=20, help="Number of reports to process in each batch.")
    args = parser.parse_args()

    update_report_summaries(args.db_path, args.batch_size)
