#!/usr/bin/env python3
"""
Safely post GitHub issue comments using temp files to handle special characters.
This script reads AI inference responses from temp files and posts them as issue comments.
"""

import os
import sys
import subprocess

def post_comment(temp_file_path, issue_number):
    """Post comment to GitHub issue using gh CLI with temp file"""
    
    try:
        # Check if temp file exists
        if not os.path.exists(temp_file_path):
            print(f"Error: Temp file {temp_file_path} not found")
            return False
        
        # Check if GH_TOKEN is available
        if not os.environ.get('GH_TOKEN'):
            print("Error: GH_TOKEN environment variable not set")
            return False
        
        # Use gh CLI to post comment from file
        cmd = ['gh', 'issue', 'comment', str(issue_number), '--body-file', temp_file_path]
        
        print(f"Posting comment to issue #{issue_number}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Comment posted successfully")
            return True
        else:
            print(f"Error posting comment: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

def main():
    """Main execution function"""
    
    # Get command line arguments
    if len(sys.argv) != 3:
        print("Usage: python3 post_comment.py <temp_file_path> <issue_number>")
        sys.exit(1)
    
    temp_file_path = sys.argv[1]
    issue_number = sys.argv[2]
    
    # Post the comment
    success = post_comment(temp_file_path, issue_number)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()