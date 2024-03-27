import pandas as pd
import sqlite3

# Load the CSV file into a DataFrame
df = pd.read_csv('./data/committee-reports-115-118.csv', skiprows=2)

# Clean up the DataFrame
df = df.dropna(subset=['Title'])  # Remove rows with missing titles
df['Congress'] = df['Congress'].str.extract('(\d+)')  # Extract the Congress number

# Create a connection to the SQLite database
conn = sqlite3.connect('politics_db.sqlite')

# Save the DataFrame to the SQLite database
df.to_sql('committee_reports', conn, if_exists='replace', index=False)

# Close the connection
conn.close()

print("Data saved to the SQLite database successfully.")
