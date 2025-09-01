#!/usr/bin/env python3
"""
Extract and truncate content from Crawl4AI response for token limit.
This script processes Crawl4AI output and prepares it for AI inference.
"""

import json
import os
import sys

def extract_content():
    """Extract content from Crawl4AI response with robust error handling"""
    
    # Get environment variables for fallback data
    crawl_outcome = os.environ.get('CRAWL_OUTCOME', '')
    fallback_url = os.environ.get('FALLBACK_URL', '')
    fallback_title = os.environ.get('FALLBACK_TITLE', '')
    
    print(f"Crawl4AI completion outcome: {crawl_outcome}")
    
    content = ""
    
    # Try to extract content from successful response
    if crawl_outcome == 'success':
        # Read raw response from temp file instead of environment variable
        temp_file = '/tmp/crawl_result_response.json'
        
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                raw_response = f.read().strip()
        except FileNotFoundError:
            print(f"Warning: Response file {temp_file} not found")
            raw_response = ""
        except Exception as e:
            print(f"Warning: Error reading response file: {e}")
            raw_response = ""
        
        if raw_response:
            try:
                response_data = json.loads(raw_response)
                print("Successfully parsed JSON response")
                print(f"Response keys: {list(response_data.keys())}")
                
                # Try multiple content fields from Crawl4AI - handle both async and sync responses
                result = response_data.get('result', {})
                results = response_data.get('results', {})
                
                # Handle results as array - get first item if it's an array
                if isinstance(results, list) and len(results) > 0:
                    print(f"Results is an array with {len(results)} items, using first item")
                    results = results[0]
                elif isinstance(results, list):
                    print("Results is an empty array")
                    results = {}
                
                # For synchronous responses, results might be at top level
                if isinstance(results, dict) and results:
                    content = (
                        results.get('fit_markdown') or
                        results.get('markdown') or
                        results.get('cleaned_html') or
                        results.get('raw_html') or
                        results.get('html') or
                        ""
                    )
                
                # For async responses, check result field
                if not content and isinstance(result, dict):
                    content = (
                        result.get('fit_markdown') or
                        result.get('markdown') or
                        result.get('cleaned_html') or
                        result.get('raw_html') or
                        result.get('html') or
                        ""
                    )
                
                if content:
                    print("Successfully extracted content from Crawl4AI response")
                else:
                    print("Warning: No content found in response data")
                    
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse JSON response: {e}")
                print(f"Response preview: {raw_response[:200]}...")
            except Exception as e:
                print(f"Warning: Unexpected error processing response: {e}")
        else:
            print("Warning: Empty response from temp file")
    else:
        print("Warning: Crawl4AI completion step was not successful or response is empty")
    
    # Use fallback if no content extracted
    if not content:
        print("Using fallback content due to extraction failure")
        content = f"URL: {fallback_url}\nTitle: {fallback_title}\nDescription: Content could not be retrieved from the URL. Please check if the URL is accessible and try again."
    
    return content

def truncate_content(content, max_length=None):
    """Safely truncate content to stay under token limit"""
    
    # Get max_length from environment variable or use default
    if max_length is None:
        max_length = int(os.environ.get('TRUNCATE_CONTENT_MAX_LENGTH', 6000))
    
    print(f"Using max_length: {max_length}")
    
    # Handle case where content might be a dict instead of string
    if isinstance(content, dict):
        print("Content is a dict, extracting raw_markdown")
        # Try to get raw_markdown or other markdown fields from dict
        content = (
            content.get('raw_markdown') or
            content.get('fit_markdown') or
            content.get('markdown') or
            content.get('cleaned_html') or
            content.get('raw_html') or
            content.get('html') or
            str(content)  # Fallback to string representation
        )
        print(f"Extracted content type: {type(content)}")
    
    # Ensure content is a string
    if not isinstance(content, str):
        print(f"Converting content from {type(content)} to string")
        content = str(content)
    
    content_length = len(content)
    print(f"Original content length: {content_length} characters")
    
    if content_length > max_length:
        truncated = content[:max_length] + "... [Content truncated to fit token limit]"
        print(f"Content truncated from {content_length} to {max_length} characters")
        return truncated
    else:
        print("Content within limit, no truncation needed")
        return content

def set_github_output(name, value):
    """Safely set GitHub Actions output"""
    
    github_output = os.environ.get('GITHUB_OUTPUT')
    if not github_output:
        print("Warning: GITHUB_OUTPUT not set")
        return
    
    delimiter = "CONTENT_EOF_DELIMITER"
    with open(github_output, 'a', encoding='utf-8') as f:
        f.write(f"{name}<<{delimiter}\n")
        f.write(value)
        f.write(f"\n{delimiter}\n")

def main():
    """Main execution function"""
    try:
        # Extract and process content
        content = extract_content()
        truncated_content = truncate_content(content)
        
        # Set output for next step
        set_github_output('content', truncated_content)
        print("Successfully set content output for AI inference")
        
    except Exception as e:
        print(f"Error: {e}")
        # Set fallback content on error
        fallback = f"URL: {os.environ.get('FALLBACK_URL', '')}\nTitle: {os.environ.get('FALLBACK_TITLE', '')}\nDescription: Error processing content."
        set_github_output('content', fallback)
        sys.exit(0)  # Don't fail the workflow, continue with fallback

if __name__ == '__main__':
    main()