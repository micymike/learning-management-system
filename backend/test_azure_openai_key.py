import os
from openai import AzureOpenAI

"""
Test your Azure OpenAI API key and deployment configuration using the AzureOpenAI client.

This script will attempt to make a simple chat completion request to your Azure OpenAI deployment
using the recommended AzureOpenAI client and explicit parameters.

Requirements:
- Set the following environment variables (in your .env or shell):
  ENDPOINT_URL (e.g., https://your-resource-name.openai.azure.com/)
  DEPLOYMENT_NAME (your deployment name, e.g., "gpt-4.1")
  AZURE_OPENAI_KEY (your Azure OpenAI subscription key)

Usage:
  python3 test_azure_openai_key.py
"""

endpoint = os.getenv("ENDPOINT_URL", "https://kidus-mafuwv4a-eastus2.cognitiveservices.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4.1")
subscription_key = os.getenv("AZURE_OPENAI_KEY", "8ZlW0fgGBZH3YfSEUJrTvgxMNuHBZ1ANPXl12MHGzURPjHnrsKWFJQQJ99BEACHYHv6XJ3w3AAAAACOGJyfI")
api_version = "2025-01-01-preview"

def main():
    print("Testing Azure OpenAI API key and deployment using AzureOpenAI client...")
    print(f"ENDPOINT_URL: {endpoint}")
    print(f"DEPLOYMENT_NAME: {deployment}")
    print(f"AZURE_OPENAI_KEY: {'set' if subscription_key else 'NOT SET'}")
    print(f"API_VERSION: {api_version}")

    try:
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=subscription_key,
            api_version=api_version,
        )

        chat_prompt = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are a helpful assistant."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Say hello."
                    }
                ]
            }
        ]

        completion = client.chat.completions.create(
            model=deployment,
            messages=chat_prompt,
            max_tokens=20,
            temperature=0.1,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False
        )

        print("SUCCESS: API key and deployment are valid.")
        print("Sample response:", completion.choices[0].message.content)
    except Exception as e:
        print("FAILED: Could not complete request.")
        print("Error:", e)

if __name__ == "__main__":
    main()
