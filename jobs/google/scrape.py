import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_google_jobs():
    # Set up headless Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run without a window
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    jobs_data = []
    page_number = 1
    
    try:
        while True:
            url = f"https://www.google.com/about/careers/applications/jobs/results?location=California%2C%20USA&page={page_number}"
            print(f"Loading page {page_number}: {url}")
            driver.get(url)
            
            # Wait for the dynamic content to load
            time.sleep(5) 

            # Locate the job cards
            job_cards = driver.find_elements(By.CSS_SELECTOR, "li.lLd3Je")

            # Check if there are no results found
            # We check both if cards are empty and if a 'no results' message might be present
            no_results_indicators = driver.find_elements(By.XPATH, "//*[contains(text(), 'no results found') or contains(text(), 'No jobs found')]")
            
            if not job_cards or len(no_results_indicators) > 0:
                print(f"No more results found on page {page_number}. Ending loop.")
                break

            print(f"Found {len(job_cards)} jobs on page {page_number}.")

            for card in job_cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h3.QJPWVe").text
                    location = card.find_element(By.CSS_SELECTOR, "span.pwO9Dc").text
                    link = card.find_element(By.CSS_SELECTOR, "a.WpHeLc").get_attribute("href")
                    jobs_data.append({
                        "Job Title": title,
                        "Location": location,
                        "Link": link
                    })
                except Exception as e:
                    continue
            
            page_number += 1
            # Safety break to avoid infinite loops if something goes wrong
            if page_number > 200:
                print("Reached safety limit of 200 pages.")
                break

    finally:
        driver.quit()
    
    return pd.DataFrame(jobs_data)

# Run and display the results
if __name__ == "__main__":
    df = scrape_google_jobs()
    if not df.empty:
        print(f"Extracted a total of {len(df)} jobs.")
        print(df.head())
        df.to_csv("workspace/scrape/jobs/google/data/google_jobs_raw.csv", index=False)
        print("Data saved to google_jobs_raw.csv")
    else:
        print("No jobs found across any pages. Check if the URL or page structure has changed.")
