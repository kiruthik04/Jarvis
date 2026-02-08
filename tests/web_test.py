import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.actions.browser import BrowserManager

def test_web_scraping():
    print("\n--- TEST: WEB SCRAPING ---")
    browser = BrowserManager()
    
    # 1. Test Google Search & URL Retrieval
    query = "DeepSeek AI features"
    print(f"Searching for: {query}")
    browser.search_google(query) # Visual check remains Google
    
    url = browser.get_first_search_result(query)
    print(f"Top Result URL: {url}")
    
    if url and url.startswith("http"):
        print("[PASS] URL Retrieval")
    else:
        print("[FAIL] URL Retrieval")
        browser.close()
        return

    # 2. Test Content Extraction
    print(f"Extracting content from: {url}")
    try:
        content = browser.extract_text(url)
        print(f"Content Length: {len(content)}")
        print(f"Snippet: {content[:200]}...")
        
        if len(content) > 100:
            print("[PASS] Content Extraction")
        else:
            print("[FAIL] Content Extraction (Too short)")
    except Exception as e:
        print(f"[FAIL] Extraction Error: {e}")

    browser.close()

if __name__ == "__main__":
    test_web_scraping()
