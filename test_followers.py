from playwright.sync_api import sync_playwright
import re

USERNAME = "creators.almanac"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(
        f"https://www.instagram.com/{USERNAME}/",
        wait_until="networkidle"
    )

    text = page.locator("body").inner_text()

    print(text[:3000])

    browser.close()