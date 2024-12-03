import pandas as pd
import time
import json
import os
from threading import Thread, Lock, current_thread
from queue import Queue, Empty
from searcher import AstroturfDetector
import logging

class AstroturfRunner:
    def __init__(self, input_file, num_threads=3):
        self.input_file = input_file
        self.num_threads = num_threads
        self.checkpoint_file = '../data/checkpoint.txt'
        self.output_file = '../data/companies_with_mentions.csv'
        
        # Thread-safe structures
        self.checkpoint_lock = Lock()
        self.csv_lock = Lock()
        self.queue = Queue()
        
        # Load data
        self.df = pd.read_json(input_file, lines=True)
        self.df['reddit_mentions_count'] = 0
        self.df['reddit_mentions'] = None
        
        # Initialize checkpoint
        self.start_index = self.load_checkpoint()
        
    def load_checkpoint(self):
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                return int(f.read().strip())
        return 0
        
    def save_checkpoint(self, index):
        with self.checkpoint_lock:
            with open(self.checkpoint_file, 'w') as f:
                f.write(str(index))
                
    def save_progress(self):
        with self.csv_lock:
            self.df.to_csv(self.output_file, index=False)
            
    def process_company(self):
        detector = AstroturfDetector()
        
        while True:
            try:
                index, company = self.queue.get_nowait()
            except Empty:
                break
                
            print(f"Thread {current_thread().name} analyzing ({index}/{len(self.df)}): {company['company_name']}")
            
            try:
                website = company['website']
                if website:
                    results = detector.detect(website)
                    print(f"Found {results['count']} Reddit mentions for {company['company_name']}")
                    
                    # Thread-safe DataFrame update
                    with self.csv_lock:
                        self.df.at[index, 'reddit_mentions_count'] = results['count']
                        self.df.at[index, 'reddit_mentions'] = json.dumps(results['mentions'])
                    
                    if results['count'] > 0:
                        for mention in results['mentions']:
                            print(f"- {mention['title']}")
                            print(f"  {mention['url']}")
                
                # Update checkpoint and save progress
                self.save_checkpoint(index + 1)
                self.save_progress()
                
            except Exception as e:
                print(f"Error processing {company['company_name']}: {str(e)}")
            
            time.sleep(4)  # Sleep between requests
            print("-" * 50 + "\n")
            
            self.queue.task_done()
            
    def run(self):
        # Fill queue with remaining companies
        for index, company in self.df.iloc[self.start_index:].iterrows():
            self.queue.put((index, company))
            
        # Start worker threads
        threads = []
        for i in range(self.num_threads):
            t = Thread(target=self.process_company, name=f"Worker-{i+1}")
            t.start()
            threads.append(t)
            
        # Wait for all threads to complete
        for t in threads:
            t.join()
            
        # Clean up checkpoint file
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
            
        print("Processing complete!")

if __name__ == "__main__":
    runner = AstroturfRunner('../data/2024-12-2-yc-companies.jl', num_threads=3)
    runner.run()