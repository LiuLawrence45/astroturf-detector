from googlesearch import search
from proxy import ProxyHandler
import requests
import time

class AstroturfDetector:
    def __init__(self):
        self.search_pages = 2  # Number of Google search pages to check
        self.results_per_page = 10
        self.proxy_handler = ProxyHandler()
    def detect(self, url: str) -> dict:
        """
        Detect potential astroturfing for a given URL by searching Reddit mentions.
        
        Args:
            url (str): The URL to check for astroturfing
        
        Returns:
            dict: Contains count of mentions and list of Reddit posts
        """

        # Sanitize and encode the URL for search
        sanitized_url = url.lower().replace('https://', '').replace('http://', '').replace('www.', '').rstrip('/')
        # encoded_url = urllib.parse.quote(sanitized_url)
        
        # Construct the Google search query
        query = f'site:reddit.com "{sanitized_url}"'
        
        MAX_RETRIES = 5
        attempts = 0
        mentions = []
        
        while attempts < MAX_RETRIES:
            try:
                # Verify current IP
                ip = requests.get('https://api.ipify.org').text
                print(f"Current IP: {ip}")
                
                # Search Google for Reddit mentions of the URL
                print(f"Searching for: {query}")
                search_results = search(
                    query,
                    num_results=self.search_pages * self.results_per_page,
                    advanced=True
                )
                
                # Process results
                for result in search_results:
                    # Check if URL appears anywhere in the description
                    if sanitized_url.lower() in result.description.lower():
                        mentions.append({
                            'url': result.url,
                            'title': result.title,
                            'description': result.description
                        })
                return {
                    'count': len(mentions),
                    'mentions': mentions
                }
            
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "too many requests" in error_msg or "blocked" in error_msg:
                    attempts += 1
                    if attempts < MAX_RETRIES:
                        print(f"\nRetrying with new proxy (attempt {attempts + 1}/{MAX_RETRIES})...")
                        if not self.proxy_handler.assign_new_proxy():
                            print("Failed to assign new proxy")
                            continue
                else:
                    print(f"\nUnexpected error: {e}")
                    return {'error': str(e), 'count': 0, 'mentions': []}

