import sqlite3
import pandas as pd
from collections import Counter
import nltk
from nltk.corpus import stopwords
import re

# Connect to the SQLite database
conn = sqlite3.connect('politics_db.sqlite')

# Fetch all report texts from the database
reports_df = pd.read_sql_query('SELECT report_text FROM committee_reports LIMIT 200', conn)

# Close the database connection
conn.close()

# Preprocess the text
def preprocess_text(text):
    if text:
        text = text.lower()
        text = re.sub(r'\W', ' ', text)
        tokens = nltk.word_tokenize(text)
        tokens = [word for word in tokens if word not in stopwords.words('english')]
        return tokens

# Get a list of all words in all reports
all_words = []
for report_text in reports_df['report_text']:
    all_words.extend(preprocess_text(report_text))

# Count the frequency of each word
word_counts = Counter(all_words)

# Filter out words that appear in more than a certain percentage of reports
threshold_percentage = 0.7
num_reports = len(reports_df)
common_words = [word for word, count in word_counts.items() if count / num_reports > threshold_percentage]

# Output the common words to a text file
with open('blacklist.txt', 'w') as file:
    for word in common_words:
        file.write(word + '\n')

print(f"Common words written to blacklist.txt")
