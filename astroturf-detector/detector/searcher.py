from googlesearch import search, SearchResult
import requests 
import time
from typing import Dict, List, Optional
from rich import print as rprint
from rich.panel import Panel
from rich.console import Console

# proxy = "http://272fa0a72b6a0f39e1f4__cr.gb,us:7dae8f8fcce7d3db@gw.dataimpulse.com:823"
# proxy2 = "http://272fa0a72b6a0f39e1f4__cr.fr,de,nl,sg,za,kr,gb,us:7dae8f8fcce7d3db@gw.dataimpulse.com:823"
proxy = "http://272fa0a72b6a0f39e1f4__cr.fr,de,nl,sg,za,kr,gb,us:7dae8f8fcce7d3db@gw.dataimpulse.com:823"

console = Console()

def search_with_retry(query: str, max_retries = 10) -> Optional[List[SearchResult]]:
    
    """
    Perform a Google search with retry logic.
    
    Args:
        query (str): The search query string
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        Optional[List[SearchResult]]: List of search results, each containing url, title, and description.
                                    Returns None if all retries fail.
    """
    
    retry_delay = 1
    for i in range(max_retries):
        try:
            # This returns a generator object
            search_results = search(query, num_results=50, proxy=proxy, advanced=True, sleep_interval=5)
            
            # Convert generator to list to process results
            results = list(search_results)
            
            console.print(f"[green]✓ Success on attempt {i + 1}![/green]")
            return results
        except Exception as e:
            console.print(f"[red]❌ Attempt {i + 1}/{max_retries} failed - {e.__class__.__name__}: {str(e):.100}...[/red]")
            
            if i < max_retries - 1:
                console.print(f"[blue]Waiting {retry_delay}s before next attempt...[/blue]")
                time.sleep(retry_delay)
                
                if retry_delay < 8:
                    retry_delay *= 2

    return None
    

def process_url(url: str, max_retries = 10) -> Dict:
    """
        Detect potential astroturfing for a given URL by searching Reddit mentions.
        
        Args:
            url (str): The URL to check for astroturfing
        
        Returns:
            dict: Dictionary containing:
                - direct_mention_count (int): Number of direct mentions found
                - direct_mentions (List[SearchResult]): List of mentions with url, title and description
                - all_search_results (List[SearchResult]): All search results returned
    """ 
    
    mentions = []
    
    # First sanitize the given URL
    sanitized_url = url.lower().replace('https://', '').replace('http://', '').replace('www.', '').rstrip('/')
    
    # What we're going to query google.
    query = f'site:reddit.com "{sanitized_url}"'
    
    search_results = search_with_retry(query = query, max_retries = max_retries)
    
    # Processing all results.
    if search_results is not None: 
        for result in search_results:
            # Check if URL appears anywhere in the description
            if sanitized_url.lower() in result.description.lower():
                mentions.append({
                    'url': result.url,
                    'title': result.title,
                    'description': result.description
                })
                # rprint(Panel(
                #     f"[green]Found mention![/green]\n"
                #     f"[blue]Title:[/blue] {result.title}\n"
                #     f"[yellow]URL:[/yellow] {result.url}\n"
                #     f"[white]Description:[/white] {result.description}",
                #     title="Reddit Mention",
                #     border_style="cyan"
                # ))
        
        
        console.print(Panel(
            f"[green]Search Results Summary[/green]\n"
            f"[blue]URL:[/blue] {url}\n"
            f"[yellow]Direct Mentions:[/yellow] {len(mentions)}\n" 
            f"[white]Total Results:[/white] {len(search_results)}",
            title="Reddit Search Results",
            border_style="green"
        ))
        return {
            'direct_mention_count': len(mentions), 
            'direct_mentions':   mentions,
            'all_search_results': search_results
        };
                
    else:
        return None
                
            



if __name__ == "__main__":
    results = process_url("https://www.undermind.ai/")
    print(results)
    