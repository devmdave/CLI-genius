#!/usr/bin/env python3
"""
CodeGen CLI - AI Powered Code Snippet Generator
Uses Hugging Face free Inference API to generate code from prompts.

Usage:
    python codegen_cli.py "Write a Python function to reverse a string"
"""

import os
import sys
import requests

# Default model (StarCoder is good for code generation)
MODEL = "bigcode/starcoder"

def query_huggingface(prompt: str, model: str = MODEL) -> str:
    """
    Query Hugging Face Inference API for code generation.
    """
    # Free endpoint (no auth required for some models, but you can set HF_TOKEN for higher limits)
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {}
    token = os.getenv("HF_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {"inputs": prompt}
    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code != 200:
        return f"Error {response.status_code}: {response.text}"

    data = response.json()
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]
    return str(data)

def main():
    if len(sys.argv) < 2:
        print("Usage: python codegen_cli.py \"<your prompt>\"")
        sys.exit(1)

    prompt = sys.argv[1]
    print(f"\n📝 Prompt: {prompt}\n")

    code_snippet = query_huggingface(prompt)
    print("💻 Generated Code:\n")
    print(code_snippet)

if __name__ == "__main__":
    main()
