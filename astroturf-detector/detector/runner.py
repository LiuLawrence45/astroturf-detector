import pandas as pd
import os
import threading 
from threading import Lock 
from typing import List
from searcher import process_url
from pandas import DataFrame
from rich.console import Console

checkpoint_lock = Lock()
results_lock = Lock() 
console_lock = Lock()
console = Console()

def save_checkpoint(checkpoint: int):
    with checkpoint_lock:
        with open('checkpoint.txt', 'w') as f:
            f.write(str(checkpoint))
            


def get_checkpoint():
    try:
        # Try to read the checkpoint file
        with open('checkpoint.txt', 'r') as f:
            checkpoint = int(f.read().strip())
            return checkpoint
    except (FileNotFoundError, ValueError):
        # File doesn't exist or contains invalid data
        # Create new file with checkpoint 0
        with open('checkpoint.txt', 'w') as f:
            f.write('0')
        return 0




def process_batch(df: DataFrame, batch_start_index: int, batch_size: int):
    """
    Process a batch of URLs concurrently, one thread per URL.
    
    Args:
        df: DataFrame containing company data
        batch_start_index: Starting index for this batch
        batch_size: Size of the batch (max 8)
    """
    
    # Edge case.
    batch_end_index = min(batch_start_index + batch_size, len(df))
    
    threads = []
    
    def process_single_url(index: int):
        """Process a single URL and update DataFrame"""
        url = df.iloc[index]['website']
        result = process_url(url, max_retries=20)  # Your URL processing function
        
        if result:
            with results_lock:
                df.at[index, 'direct_mentions_count'] = result.get('direct_mentions_count')
                df.at[index, 'direct_mentions'] = str(result.get('mentions'))
                df.at[index, 'all_search_results'] = str(result.get('all_search_results'))
                
        else:
            with console_lock:
                console.print(f"[red]❌ All 20 attempts failed for URL: {url}[/red]")
    
    # Create and start a thread for each URL in the batch
    for i in range(batch_start_index, batch_end_index):
        thread = threading.Thread(target=process_single_url, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads in this batch to complete
    for thread in threads:
        thread.join()
    save_checkpoint(batch_end_index)
    return df

if __name__ == "__main__":
    
    # df = pd.read_csv('input.csv')
    # df = df[['company_name', 'short_description','website']]
    # df.to_csv('minimal_input.csv', index=False)
    df = pd.read_csv('results/default.csv')
    df = df.head(8)
    checkpoint = get_checkpoint()
    print(f"Checkpoint is: ", checkpoint)
    amount = int(input("Enter the amount you want to process (multiple of 8): "))
    
    end_index = checkpoint + amount
    batch_size = 4
    for i in range(checkpoint, end_index, batch_size):
        process_batch(df, checkpoint, batch_size);
        df.to_csv(f"results/batch_{checkpoint}_{i+batch_size}")
    
    # df = df.head(8)
    # print(df)
    # checkpoint = get_checkpoint()
    # print(f"Starting from checkpoint: {checkpoint}")
    # process_batch(df, checkpoint, 4)
