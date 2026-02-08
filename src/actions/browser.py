from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from ..config import Config
import time
import requests
from bs4 import BeautifulSoup
import re
import os

class BrowserManager:
    def __init__(self):
        self.driver = None 

    def _ensure_driver(self):
        """
         Checks if driver is active. If not, initializes it.
        """
        if self.driver:
            # Check if session is valid
            try:
                self.driver.current_url
                return
            except:
                print("Browser session lost. Restarting...")
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

        print("Initializing Browser...")
        options = webdriver.ChromeOptions()
        # if Config.HEADLESS_BROWSER:
        #     options.add_argument("--headless")
        options.add_argument("--start-maximized")
        # Keep browser open after script ends might be desired for debugging
        options.add_experimental_option("detach", True) 
        
        # Anti-Detection & Persistence
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # User Data Dir (Persist Cookies to avoid repeated CAPTCHAs)
        # Using a local 'browser_profile' folder in the project root
        profile_path = os.path.join(os.getcwd(), "browser_profile")
        options.add_argument(f"user-data-dir={profile_path}")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Additional Patch
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def open_url(self, url):
        self._ensure_driver()
        print(f"Opening URL: {url}")
        self.driver.get(url)

    def search_google(self, query):
        """
        Opens Search (DuckDuckGo) in the browser (visual only).
        Using DDG to avoid visual CAPTCHAs for the user.
        """
        self._ensure_driver()
        print(f"Opening Search for: {query}")
        self.driver.get("https://duckduckgo.com")
        try:
            # Try finding the search box
            try:
                search_box = self.driver.find_element(By.NAME, "q")
            except:
                 try:
                    search_box = self.driver.find_element(By.ID, "search_form_input")
                 except:
                    # Direct URL fallback
                    self.driver.get(f"https://duckduckgo.com/?q={query}")
                    return self.driver.current_url

            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            # Wait for results to load
            time.sleep(2)
            return self.driver.current_url
        except Exception as e:
            print(f"Error searching: {e}")
            return None

    def get_first_search_result(self, query):
        """
        Uses DuckDuckGo to search and retrieve the first organic result URL.
        DuckDuckGo is often easier to scrape programmatically than Google.
        """
        try:
            self._ensure_driver()
            print(f"Searching DuckDuckGo for: {query}")
            self.driver.get("https://duckduckgo.com")
            try:
                # DDG Home Search Box
                search_box = self.driver.find_element(By.NAME, "q")
            except:
                # Sometimes DDG redirects to search result page directly or has different ID
                 try:
                    search_box = self.driver.find_element(By.ID, "search_form_input")
                 except:
                    # Fallback to URL manipulation if input not found
                    self.driver.get(f"https://duckduckgo.com/?q={query}")
                    time.sleep(3)
                    return self._extract_ddg_link()

            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3) # Wait for load
            
            return self._extract_ddg_link()

        except Exception as e:
            print(f"Failed to get search result: {e}")
            return None

    def _extract_ddg_link(self):
        # Find first result
        # DDG selectors: a[data-testid="result-title-a"]
        try:
            results = self.driver.find_elements(By.CSS_SELECTOR, "a[data-testid='result-title-a']")
            if results:
                return results[0].get_attribute("href")
            
            # Fallback selector
            results = self.driver.find_elements(By.CSS_SELECTOR, ".result__a")
            if results:
                return results[0].get_attribute("href")
        except:
            pass
        return None

    def extract_text(self, url):
        """
        Fetches the URL using requests and extracts main text using BeautifulSoup.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Extract text
            text = soup.get_text()

            # Clean text (remove extra whitespace)
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit header
            return clean_text[:4000] # Return first 4000 chars for LLM context limits
        except Exception as e:
            return f"Error extracting text: {e}"

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
