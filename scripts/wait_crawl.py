#!/usr/bin/env python3
"""
Wait for Crawl4AI task completion with robust error handling.
This script polls a Crawl4AI task until completion and sets GitHub Actions output.
"""

import json
import os
import time
import requests

def wait_for_completion():
    """Wait for Crawl4AI task completion with robust error handling"""
    
    # Read raw response from temp file instead of environment variable
    temp_file = '/tmp/crawl_submit_response.json'
    
    try:
        with open(temp_file, 'r', encoding='utf-8') as f:
            raw_response = f.read().strip()
    except FileNotFoundError:
        print(f"Error: Response file {temp_file} not found")
        return None
    except Exception as e:
        print(f"Error reading response file: {e}")
        return None
    
    print(f"Raw response from crawl submit (length: {len(raw_response)} chars)")
    
    if not raw_response:
        print("Error: Empty response from crawl submit")
        return None
    
    try:
        response_data = json.loads(raw_response)
        task_id = response_data.get('task_id')
        
        if not task_id:
            print(f"Error: No task_id in response: {list(response_data.keys())}")
            return None
        
        print(f"Successfully extracted task_id: {task_id}")
        
        # Poll for completion (max 60 seconds)
        for attempt in range(1, 13):
            try:
                response = requests.get(f"http://localhost:11235/task/{task_id}", timeout=10)
                
                if response.status_code != 200:
                    print(f"Attempt {attempt}: HTTP {response.status_code}")
                    time.sleep(5)
                    continue
                
                task_data = response.json()
                status = task_data.get('status', 'unknown')
                print(f"Attempt {attempt}: Task status: {status}")
                
                if status == 'completed':
                    print("Task completed successfully")
                    return task_data
                elif status == 'failed':
                    error_msg = task_data.get('error', 'No error details')
                    print(f"Task failed: {error_msg}")
                    return None
                
                time.sleep(5)
                
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt}: Request failed: {e}")
                time.sleep(5)
                continue
            except json.JSONDecodeError as e:
                print(f"Attempt {attempt}: Invalid JSON response: {e}")
                time.sleep(5)
                continue
        
        print("Task timeout after 60 seconds")
        return None
        
    except json.JSONDecodeError as e:
        print(f"Error parsing crawl submit response: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def set_github_output(name, value):
    """Set GitHub Actions output"""
    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            delimiter = "RESPONSE_EOF"
            f.write(f"{name}<<{delimiter}\n")
            f.write(value)
            f.write(f"\n{delimiter}\n")

def main():
    """Main execution function"""
    try:
        result = wait_for_completion()
        if result:
            set_github_output('response', json.dumps(result))
            print("Successfully set response output")
        else:
            print("Failed to get valid response, continuing with empty result")
            set_github_output('response', '{}')
    except Exception as e:
        print(f"Error in wait_for_completion: {e}")
        set_github_output('response', '{}')

if __name__ == '__main__':
    main()