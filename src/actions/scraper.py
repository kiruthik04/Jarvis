import requests
from bs4 import BeautifulSoup

class WebScraper:
    def scrape_text(self, url):
        """
        Fetches the content of a URL and returns the text.
        """
        try:
            print(f"Scraping: {url}")
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Kill all script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text[:5000] # Return first 5000 chars to avoid overload
        except Exception as e:
            return f"Error scraping {url}: {e}"

    def get_links(self, url):
        """Returns all hrefs from a page."""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            for a in soup.find_all('a', href=True):
                links.append(a['href'])
            return links
        except Exception as e:
            return []
