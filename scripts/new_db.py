import pandas as pd
import sqlite3

df = pd.read_csv('./data/gics-map-2018.csv')

conn = sqlite3.connect('./data/industry_db.sqlite')

df.to_sql('industries', conn, if_exists='replace', index=False)

conn.close()

print("Database created successfully!")
