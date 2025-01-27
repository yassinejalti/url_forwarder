from flask import Flask, request, Response
import requests
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return {"status": "running"}, 200

@app.route('/download-pdf', methods=['GET'])
def download_pdf():
    try:
        pdf_url = request.args.get('pdf_url')

        if not pdf_url:
            return {"error": "PDF URL is required as a query parameter (e.g., ?pdf_url=...)"}, 400

        response = requests.get(pdf_url, stream=True)

        if response.status_code != 200:
            return {"error": f"Failed to fetch PDF: {response.status_code}"}, response.status_code

        pdf_bytes = BytesIO(response.content)

        return Response(
            pdf_bytes.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': 'inline; filename="displayed-pdf.pdf"',
                'Content-Type': 'application/pdf'
            }
        )

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0')
