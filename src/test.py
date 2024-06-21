from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

def is_valid_linkedin_url(url):
    chrome_driver_path = '/usr/local/bin/chromedriver'
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = None
    try:
        # Set up the webdriver
        service = ChromeService(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Open the URL
        driver.get(url)
        
        # Check if the title contains 'LinkedIn'
        if 'LinkedIn' in driver.title:
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        if driver:
            driver.quit()

# Example usage
url = "https://www.linkedin.com/in/your-profile"
is_valid = is_valid_linkedin_url(url)
print(f"The URL is {'valid' if is_valid else 'invalid'}")
