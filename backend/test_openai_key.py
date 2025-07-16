#!/usr/bin/env python3
"""Test script to verify both Azure and standard OpenAI API keys"""

import os
import sys
from dotenv import load_dotenv
import openai

def test_azure_openai_key():
    # Get Azure API key
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    api_version = os.getenv("OPENAI_API_VERSION", "2023-05-15")
    deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
    
    if not all([api_key, api_base, deployment_name]):
        print("ERROR: Missing Azure OpenAI configuration")
        return False
    
    # Test the Azure key
    try:
        client = openai.AzureOpenAI(
            api_key=api_key,
            azure_endpoint=api_base,
            api_version=api_version
        )
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print(f"SUCCESS: Azure OpenAI API key is valid.")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"ERROR: Azure OpenAI API key validation failed: {e}")
        return False

def test_standard_openai_key():
    # Get standard OpenAI API key
    api_key = os.getenv("STANDARD_OPENAI_API_KEY")
    
    if not api_key:
        print("ERROR: STANDARD_OPENAI_API_KEY not found in environment variables")
        return False
    
    # Test the standard OpenAI key
    try:
        client = openai.OpenAI(api_key=api_key)
        models = client.models.list()
        print(f"SUCCESS: Standard OpenAI API key is valid. Available models:")
        for model in models.data[:3]:  # Show first 3 models
            print(f"- {model.id}")
        return True
    except Exception as e:
        print(f"ERROR: Standard OpenAI API key validation failed: {e}")
        return False

def test_process_with_azure_openai():
    from agents.orchestrator import process_with_azure_openai
    print("\n=== Testing process_with_azure_openai ===")
    repo = "https://github.com/example/repo"
    prompt = "Summarize the main functionality of this repository."
    result = process_with_azure_openai(repo, prompt)
    print("Result from process_with_azure_openai:", result)

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    print("=== Testing Azure OpenAI API Key ===")
    azure_success = test_azure_openai_key()
    
    print("\n=== Testing Standard OpenAI API Key ===")
    standard_success = test_standard_openai_key()
    
    test_process_with_azure_openai()
    
    if azure_success and standard_success:
        print("\nBoth API keys are valid!")
        sys.exit(0)
    elif azure_success:
        print("\nOnly Azure OpenAI API key is valid.")
        sys.exit(1)
    elif standard_success:
        print("\nOnly Standard OpenAI API key is valid.")
        sys.exit(1)
    else:
        print("\nBoth API keys are invalid.")
        sys.exit(1)
