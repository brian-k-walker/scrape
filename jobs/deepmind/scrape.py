import csv
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://job-boards.greenhouse.io/deepmind"


def scrape_deepmind_to_csv(filename="jobs/deepmind/data/deepmind_raw.csv"):
    all_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        page_num = 1
        while True:
            url = f"{BASE_URL}?page={page_num}" if page_num > 1 else BASE_URL
            page.goto(url, wait_until="networkidle", timeout=30000)
            print(f"Scraping page {page_num}...")

            if not page.query_selector("tr.job-post"):
                break

            jobs = page.evaluate("""() => {
                const rows = document.querySelectorAll('tr.job-post');
                const results = [];
                rows.forEach(row => {
                    const link = row.querySelector('a[href*="/jobs/"]');
                    if (!link) return;
                    const titleEl = link.querySelector('p.body--medium');
                    const locEl = link.querySelector('p.body--metadata');
                    const section = row.closest('section');
                    const deptEl = section ? section.querySelector('h3') : null;
                    results.push({
                        Title: titleEl ? titleEl.textContent.trim() : link.textContent.trim(),
                        Department: deptEl ? deptEl.textContent.trim() : '',
                        Location: locEl ? locEl.textContent.trim() : '',
                        URL: link.href
                    });
                });
                return results;
            }""")

            if not jobs:
                break

            all_jobs.extend(jobs)
            print(f"  Found {len(jobs)} jobs on page {page_num}")
            page_num += 1

        browser.close()

    if all_jobs:
        keys = all_jobs[0].keys()
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_jobs)
        print(f"Done! {len(all_jobs)} jobs saved to {filename}")
    else:
        print("No jobs found.")


if __name__ == "__main__":
    scrape_deepmind_to_csv()
