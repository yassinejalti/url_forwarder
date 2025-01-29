from flask import Flask, request, Response, jsonify
import requests
from io import BytesIO
from flask_cors import CORS
import random
import logging
import time

# Setup Flask
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# List of user-agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/88.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/537.36"
]

def get_random_headers():
    """Generate random headers to avoid detection."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/pdf,application/json;q=0.9,image/webp,*/*;q=0.8",
        "DNT": "1",  # Do Not Track
        "Upgrade-Insecure-Requests": "1"
    }

@app.route('/', methods=['GET'])
def index():
    logging.info("Health check endpoint hit.")
    return {"status": "running"}, 200

@app.route('/download-pdf', methods=['GET'])
def download_pdf():
    try:
        pdf_url = request.args.get('pdf_url')

        if not pdf_url:
            logging.warning("Missing 'pdf_url' query parameter.")
            return jsonify({"error": "PDF URL is required"}), 400

        logging.info(f"Attempting to fetch PDF from: {pdf_url}")

        for attempt in range(3):  # Retry up to 3 times
            try:
                headers = get_random_headers()
                logging.info(f"Attempt {attempt + 1}: Using headers: {headers}")

                response = requests.get(pdf_url, headers=headers, stream=True, timeout=10)

                if response.status_code == 200 and 'pdf' in response.headers.get('Content-Type', '').lower():
                    logging.info("PDF successfully fetched!")
                    pdf_bytes = BytesIO(response.content)
                    return Response(
                        pdf_bytes.getvalue(),
                        mimetype='application/pdf',
                        headers={"Content-Disposition": 'inline; filename="displayed-pdf.pdf"'}
                    )

                logging.warning(f"Failed attempt {attempt + 1}, Status: {response.status_code}")

            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}")

            time.sleep(random.uniform(1, 3))  # Random delay before retry

        return jsonify({"error": "Failed to fetch PDF after multiple attempts"}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
