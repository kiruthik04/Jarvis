from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from ..config import Config
import time

class BrowserManager:
    def __init__(self):
        options = webdriver.ChromeOptions()
        # if Config.HEADLESS_BROWSER:
        #     options.add_argument("--headless")
        options.add_argument("--start-maximized")
        # Keep browser open after script ends might be desired for debugging
        options.add_experimental_option("detach", True) 
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def open_url(self, url):
        print(f"Opening URL: {url}")
        self.driver.get(url)

    def search_google(self, query):
        print(f"Searching Google for: {query}")
        self.driver.get("https://www.google.com")
        try:
            search_box = self.driver.find_element(By.NAME, "q")
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            # Wait for results to load
            time.sleep(2)
            return self.driver.current_url
        except Exception as e:
            print(f"Error searching Google: {e}")
            return None

    def close(self):
        self.driver.quit()
