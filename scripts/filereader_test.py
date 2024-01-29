import os
import PyPDF2
import requests

def read_pdf_from_url(url):
    response = requests.get(url)
    with open('temp.pdf', 'wb') as file:
        file.write(response.content)

    with open('temp.pdf', 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        num_pages = pdf_reader.numPages
        for page_num in range(num_pages):
            page = pdf_reader.getPage(page_num)
            text = page.extractText()
            print(f"Page {page_num + 1}: {text}")

    # Clean up the temporary file
    os.remove('temp.pdf')

# Example usage
url = 'https://api.congress.gov/v3/committee-report/117/HRPT/463?api_key=Gej1jav3dg99KkJbAqneBc40kxt7pbeyODF9r1Tt?format=json'
read_pdf_from_url(url)
