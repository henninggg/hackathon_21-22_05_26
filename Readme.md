python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# after some installments:
pip freeze > requirements.txt

# run webscraping
ORIQX_EMAIL=you@email.com ORIQX_PASSWORD=yourpassword python scrape_docs.py


# work on a feature
git checkout feature/lll-reduction
# ... code ...
git add . && git commit -m "add LLL basis reduction"
git push origin feature/lll-reduction

# merge into dev when it works
git checkout dev
git merge feature/lll-reduction
git push origin dev

# merge into main when demo-ready
git checkout main
git merge dev
git push origin main