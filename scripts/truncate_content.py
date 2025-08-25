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
    
    # Get environment variables
    crawl_outcome = os.environ.get('CRAWL_OUTCOME', '')
    raw_response = os.environ.get('RAW_RESPONSE', '')
    fallback_url = os.environ.get('FALLBACK_URL', '')
    fallback_title = os.environ.get('FALLBACK_TITLE', '')
    
    print(f"Crawl4AI completion outcome: {crawl_outcome}")
    
    content = ""
    
    # Try to extract content from successful response
    if crawl_outcome == 'success' and raw_response:
        try:
            response_data = json.loads(raw_response)
            print("Successfully parsed JSON response")
            
            # Try multiple content fields from Crawl4AI
            result = response_data.get('result', {})
            content = (
                result.get('fit_markdown') or
                result.get('markdown') or
                result.get('cleaned_html') or
                result.get('raw_html') or
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
        print("Warning: Crawl4AI completion step was not successful or response is empty")
    
    # Use fallback if no content extracted
    if not content:
        print("Using fallback content due to extraction failure")
        content = f"URL: {fallback_url}\nTitle: {fallback_title}\nDescription: Content could not be retrieved from the URL. Please check if the URL is accessible and try again."
    
    return content

def truncate_content(content, max_length=6000):
    """Safely truncate content to stay under token limit"""
    
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