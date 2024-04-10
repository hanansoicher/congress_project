import pandas as pd
import sqlite3

df = pd.read_csv('./data/committee-reports-115-118.csv', skiprows=2)
df = df.dropna(subset=['Title'])
df['Congress'] = df['Congress'].str.extract('(\d+)')

conn = sqlite3.connect('politics_db.sqlite')

df.to_sql('committee_reports', conn, if_exists='replace', index=False)

conn.close()
print("Data saved to the SQLite database successfully.")
