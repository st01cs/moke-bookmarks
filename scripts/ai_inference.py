#!/usr/bin/env python3
"""
Custom AI inference script supporting multiple providers.
Supports OpenAI, Anthropic, and other OpenAI-compatible APIs.
"""

import json
import os
import sys
import requests
from typing import Optional, Dict, Any

def load_system_prompt(file_path: str) -> str:
    """Load system prompt from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error loading system prompt: {e}")
        return ""

def load_user_prompt() -> str:
    """Load user prompt from environment or stdin"""
    # Try to get from environment first (for workflow usage)
    prompt = os.environ.get('USER_PROMPT', '')
    if prompt:
        return prompt
    
    # Fall back to stdin for interactive usage
    try:
        return sys.stdin.read().strip()
    except Exception as e:
        print(f"Error reading prompt: {e}")
        return ""

def call_openai_api(api_key: str, base_url: str, model: str, system_prompt: str, user_prompt: str, max_tokens: int) -> Optional[str]:
    """Call OpenAI-compatible API"""
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        'max_tokens': max_tokens,
        'temperature': 0.7
    }
    
    try:
        response = requests.post(f"{base_url}/chat/completions", 
                               headers=headers, 
                               json=data, 
                               timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Unexpected API response format: {e}")
        return None

def call_anthropic_api(api_key: str, model: str, system_prompt: str, user_prompt: str, max_tokens: int) -> Optional[str]:
    """Call Anthropic API"""
    
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
    }
    
    data = {
        'model': model,
        'system': system_prompt,
        'messages': [
            {'role': 'user', 'content': user_prompt}
        ],
        'max_tokens': max_tokens
    }
    
    try:
        response = requests.post('https://api.anthropic.com/v1/messages', 
                               headers=headers, 
                               json=data, 
                               timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result['content'][0]['text']
        
    except requests.exceptions.RequestException as e:
        print(f"Anthropic API request failed: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Unexpected Anthropic API response format: {e}")
        return None

def set_github_output(name: str, value: str):
    """Set GitHub Actions output"""
    github_output = os.environ.get('GITHUB_OUTPUT')
    if not github_output:
        print(f"Warning: GITHUB_OUTPUT not set, would set {name}")
        return
    
    delimiter = f"{name.upper()}_EOF_DELIMITER"
    with open(github_output, 'a', encoding='utf-8') as f:
        f.write(f"{name}<<{delimiter}\n")
        f.write(value)
        f.write(f"\n{delimiter}\n")

def main():
    """Main execution function"""
    
    # Get configuration from environment
    provider = os.environ.get('AI_PROVIDER', '').lower()
    api_key = os.environ.get('AI_API_KEY', '')
    base_url = os.environ.get('AI_BASE_URL', 'https://api.openai.com/v1')
    model = os.environ.get('AI_MODEL', 'gpt-3.5-turbo')
    max_tokens = int(os.environ.get('AI_MAX_TOKENS', '2000'))
    system_prompt_file = os.environ.get('SYSTEM_PROMPT_FILE', '')
    
    print(f"AI Provider: {provider}")
    print(f"Model: {model}")
    print(f"Max tokens: {max_tokens}")
    print(f"Base URL: {base_url}")
    
    # Validate configuration
    if not provider:
        print("Error: AI_PROVIDER not specified")
        sys.exit(1)
    
    if not api_key:
        print("Error: AI_API_KEY not specified")
        sys.exit(1)
    
    if not system_prompt_file:
        print("Error: SYSTEM_PROMPT_FILE not specified")
        sys.exit(1)
    
    # Load prompts
    system_prompt = load_system_prompt(system_prompt_file)
    if not system_prompt:
        print("Error: Failed to load system prompt")
        sys.exit(1)
    
    user_prompt = load_user_prompt()
    if not user_prompt:
        print("Error: No user prompt provided")
        sys.exit(1)
    
    print(f"System prompt length: {len(system_prompt)} chars")
    print(f"User prompt length: {len(user_prompt)} chars")
    
    # Call appropriate API
    response = None
    
    if provider == 'openai' or provider == 'custom':
        response = call_openai_api(api_key, base_url, model, system_prompt, user_prompt, max_tokens)
    elif provider == 'anthropic':
        response = call_anthropic_api(api_key, model, system_prompt, user_prompt, max_tokens)
    else:
        print(f"Error: Unsupported provider '{provider}'. Supported: openai, anthropic, custom")
        sys.exit(1)
    
    # Handle response
    if response:
        print("AI inference completed successfully")
        print(f"Response length: {len(response)} chars")
        set_github_output('response', response)
    else:
        print("Error: AI inference failed")
        fallback_response = "AI inference failed. Please check your API configuration."
        set_github_output('response', fallback_response)
        sys.exit(1)

if __name__ == '__main__':
    main()