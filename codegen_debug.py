#!/usr/bin/env python3
"""
CodeGen CLI - AI Powered Code Snippet Generator
Uses Hugging Face free Inference API to generate code from prompts.

Usage:
    python codegen_debug.py generate "Write a Python function to reverse a string" [--api-key KEY]
    python codegen_debug.py set-key YOUR_API_KEY
"""

import argparse
import os
import subprocess
from huggingface_hub import InferenceClient
from extractor import extract_code
from extractor import save_code_interactive
from extractor import generate_filename_from_prompt
from extractor import detect_extension


def main():
    parser = argparse.ArgumentParser(description="Generate code snippets from prompts using AI.")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate code from prompt')
    gen_parser.add_argument('prompt', help='The prompt to generate code from.')
    gen_parser.add_argument('--api-key', help='Hugging Face API key (optional, overrides env var)')

    # Set key command
    set_parser = subparsers.add_parser('set-key', help='Set the Hugging Face API key persistently')
    set_parser.add_argument('key', help='The API key to set')

    args = parser.parse_args()

    if args.command == 'set-key':
        try:
            subprocess.run(['setx', 'HF_API_KEY', args.key], check=True)
            print("API key set successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error setting API key: {e}")
    elif args.command == 'generate':
        api_key = args.api_key or os.getenv("HF_API_KEY")
        if not api_key:
            print("Error: API key not provided. Use --api-key or set HF_API_KEY environment variable.")
            return

        client = InferenceClient(api_key=api_key)

        try:
            completion = client.chat.completions.create(
                model="Qwen/Qwen3-32B:groq",
                messages=[
                    {
                        "role": "user",
                        "content": args.prompt
                    }
                ],
            )
            filename = generate_filename_from_prompt(args.prompt, detect_extension(args.prompt))
            code_snippet = extract_code(completion.choices[0].message.content)
            print(code_snippet)
            save_code_interactive(code_snippet, filename)

        except Exception as e:
            print(f"Error generating code: {e}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()