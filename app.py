from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    # Connect to your SQLite database and perform the search
    conn = sqlite3.connect('politics_db.sqlite')
    cur = conn.cursor()
    cur.execute("SELECT * FROM committee_reports WHERE report_text LIKE ? OR Title LIKE ?", ('%'+query+'%', '%'+query+'%'))
    results = cur.fetchall()
    conn.close()
    return render_template('results.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)
