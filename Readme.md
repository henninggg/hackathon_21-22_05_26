python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# after some installments:
pip freeze > requirements.txt

# run webscraping
ORIQX_EMAIL=you@email.com ORIQX_PASSWORD=yourpassword python scrape_docs.py