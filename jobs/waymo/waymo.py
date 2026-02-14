import csv
import time
from playwright.sync_api import sync_playwright

def scrape_waymo_to_csv(base_url, filename="workspace/scrape/jobs/waymo/data/waymo_jobs_raw.csv"):
    all_jobs = []
    page_number = 1
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        while True:
            current_url = f"{base_url}&page={page_number}"
            print(f"Scraping Page {page_number}...")
            
            try:
                page.goto(current_url, wait_until="networkidle", timeout=15000)
                page.wait_for_selector('div.job-search-results-card', timeout=7000)
            except Exception as e:
                print(f"Finished at page {page_number-1}.", e)
                break

            job_cards = page.query_selector_all('div.job-search-results-card')
            if not job_cards:
                print(f"Uh-oh. No jobs found on page {page_number}.")
                break

            for card in job_cards:
                # Prefer the actual job title link inside the card
                title_el = card.query_selector('h3.card-title a') or card.query_selector('h3 a') or card.query_selector('a[id^="link_job_title_"]')

                # Prefer structured location/department blocks (can be multiple locations)
                location_spans = card.query_selector_all('.job-component-list-location .job-component-location span')
                dept_span = card.query_selector('.job-component-list-department .job-component-department span')

                # Fallback: some variants put the canonical URL in a footer link
                footer_link = card.query_selector('div.job-search-results-footer a')

                # Broad fallback for any remaining metadata
                meta_spans = card.query_selector_all('span')
                
                if title_el:
                    title = title_el.inner_text().strip()

                    locations = [s.inner_text().strip() for s in location_spans if s.inner_text().strip()]
                    location = " | ".join(locations) if locations else "California"

                    department = dept_span.inner_text().strip() if dept_span and dept_span.inner_text().strip() else "N/A"

                    href = (title_el.get_attribute("href") if title_el else "") or (footer_link.get_attribute("href") if footer_link else "")
                    url = href if href and href.startswith("http") else ("https://careers.withwaymo.com" + href if href else "")

                    # Clean up metadata (fallback only)
                    meta_text = [m.inner_text().strip() for m in meta_spans if m.inner_text().strip()]
                    if department == "N/A" and meta_text:
                        department = meta_text[0]
                    if location == "California" and len(meta_text) > 1:
                        location = meta_text[1]

                    job_data = {
                        "Title": title,
                        "Department": department,
                        "Location": location,
                        "URL": url
                    }
                    all_jobs.append(job_data)

            page_number += 1
            time.sleep(1) 
        browser.close()

    # --- Write to CSV ---
    if all_jobs:
        keys = all_jobs[0].keys()  # Get column headers from the first dictionary
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_jobs)
        print(f"✅ Success! {len(all_jobs)} jobs saved to {filename}")
    else:
        print("❌ No jobs were found.")

# Base URL from your search filters
base_filtered_url = "https://careers.withwaymo.com/jobs/search?department_uids%5B%5D=9edee38059d1b1ce766fe8312f3bc75e&department_uids%5B%5D=451e57010e816b71a8312792faf5740f&department_uids%5B%5D=19d17c748ffd57fdd1b8b34510a5ee10&department_uids%5B%5D=fdbec1fdc0be4cd648517ace2b6b0a45&employment_type_uids%5B%5D=2ea50d7de0fbb2247d09474fbb5ee4da&country_codes%5B%5D=US&states%5B%5D=California&query="

if __name__ == "__main__":
    scrape_waymo_to_csv(base_filtered_url)