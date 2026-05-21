import os
from playwright.sync_api import sync_playwright
import html2text

EMAIL = os.environ.get("ORIQX_EMAIL", "your@email.com")
PASSWORD = os.environ.get("ORIQX_PASSWORD", "yourpassword")
DOCS_URL = "https://app.oriqx.com/docs"
OUTPUT_FILE = "oriqx_docs.md"

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False so you can see/debug
        page = browser.new_page()

        print("Navigating to login...")
        page.goto("https://app.oriqx.com/login")
        page.wait_for_load_state("networkidle")

        # Fill login form — adjust selectors if needed
        page.fill('input[type="email"]', EMAIL)
        page.fill('input[type="password"]', PASSWORD)
        page.click('button[type="submit"]')

        page.wait_for_load_state("networkidle")
        print("Logged in, navigating to docs...")

        page.goto(DOCS_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)  # wait for JS to render

        html = page.content()
        browser.close()

    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    markdown = converter.handle(html)

    with open(OUTPUT_FILE, "w") as f:
        f.write(markdown)

    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape()
