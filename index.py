from flask import Flask, request, Response, jsonify
import requests
from io import BytesIO
from flask_cors import CORS
import logging

# Setup Flask
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET'])
def index():
    logging.info("Health check endpoint hit.")
    return {"status": "running"}, 200

@app.route('/download-pdf', methods=['GET'])
def download_pdf():
    try:
        logging.info("Received request for PDF download.")
        
        pdf_url = request.args.get('pdf_url')

        if not pdf_url:
            logging.warning("Missing 'pdf_url' query parameter.")
            return jsonify({"error": "PDF URL is required as a query parameter (e.g., ?pdf_url=...)"}), 400

        logging.info(f"Fetching PDF from URL: {pdf_url}")
        response = requests.get(pdf_url, stream=True)

        logging.info(f"Received response: Status Code = {response.status_code}")
        logging.debug(f"Response Headers: {response.headers}")

        if response.status_code != 200:
            logging.error(f"Failed to fetch PDF. Status code: {response.status_code}")
            return jsonify({"error": f"Failed to fetch PDF: {response.status_code}"}), response.status_code

        # Check response content type
        content_type = response.headers.get('Content-Type', '')
        logging.info(f"Response Content-Type: {content_type}")

        if 'pdf' not in content_type.lower():
            logging.warning("Response is not a valid PDF.")
            return jsonify({"error": "The requested URL did not return a PDF."}), 400

        # Debug response content length
        content_length = response.headers.get('Content-Length', 'Unknown')
        logging.info(f"Response Content-Length: {content_length}")

        pdf_bytes = BytesIO(response.content)

        logging.info("Successfully fetched and processed the PDF.")

        return Response(
            pdf_bytes.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': 'inline; filename="displayed-pdf.pdf"',
                'Content-Type': 'application/pdf'
            }
        )

    except requests.exceptions.RequestException as req_err:
        logging.error(f"RequestException occurred: {str(req_err)}")
        return jsonify({"error": f"Request failed: {str(req_err)}"}), 500

    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
