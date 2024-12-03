
# 823 is http
# curl -x "http://272fa0a72b6a0f39e1f4:7dae8f8fcce7d3db@gw.dataimpulse.com:823" https://api.ipify.org/


# https://oxylabs.io/blog/python-requests-retry
import requests
import time
# from requests.adapters import HTTPAdapter 
# from urllib3.util import Retry 

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

USERNAME = "272fa0a72b6a0f39e1f4"
PASSWORD = "7dae8f8fcce7d3db"

url = "https://api.ipify.org"

proxies = {
    "http": f"http://{USERNAME}:{PASSWORD}@gw.dataimpulse.com:823",
    "https": f"http://{USERNAME}:{PASSWORD}@gw.dataimpulse.com:823"
}

console = Console()

# Fancy print. That's the only difference.
def get_with_retries(url, proxies, max_retries=5, initial_delay=1):
    retry_delay = initial_delay

    for i in range(max_retries):
        try:
            response = requests.get(url, proxies=proxies, timeout=10)
            response.raise_for_status()
            console.print(f"[green]✓ Success on attempt {i + 1}![/green]")
            return response
        except requests.exceptions.RequestException as e:
            console.print(Panel(
                f"[red]Attempt {i + 1}/{max_retries} failed[/red]\n"
                f"[yellow]Error Type:[/yellow] {e.__class__.__name__}\n"
                f"[yellow]Details:[/yellow] {str(e)}",
                title="Error Details",
                border_style="red"
            ))
            
            if i < max_retries - 1:
                console.print(f"[blue]Waiting {retry_delay}s before next attempt...[/blue]")
                time.sleep(retry_delay)
                retry_delay *= 2

    return None

for _ in range(10):
    response = get_with_retries(url, proxies = proxies)
    print(response.text)
    time.sleep(2)