#!/usr/bin/env python3
"""
CLI Genius - AI Powered Console Assistant (Gemini Edition)

Features:
- Interactive REPL with Gemini
- Persistent conversation context (per session)
- Logs all Q&A to cli_genius.log
- Flags for model selection and temperature
- Multi-line input with triple quotes
- Colorized output
- Shell command integration with ! prefix
- Gemini API key management via flags
"""

import os
import sys
import google.generativeai as genai
import readline
import subprocess
from datetime import datetime

LOG_FILE = "cli_genius.log"

# -----------------------------
# Config
# -----------------------------
def configure_gemini(model_name: str, temperature: float):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set. Use:\n")
        print("   ./cli_genius.py --set-gemini-key <YOUR_KEY>\n")
        sys.exit(1)
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name), temperature

# -----------------------------
# Helpers
# -----------------------------
def log_interaction(user_input: str, response: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now()}]\nYou> {user_input}\nGemini> {response}\n")

def run_shell_command(cmd: str) -> str:
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"Error running command: {e}"

def colorize(text: str, color: str = "green") -> str:
    colors = {
        "green": "\033[92m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color,'')}{text}{colors['reset']}"

# -----------------------------
# Main Loop
# -----------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="CLI Genius - Gemini Assistant")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Gemini model (e.g. gemini-1.5-pro)")
    parser.add_argument("--temp", type=float, default=0.7, help="Response creativity (0.0-1.0)")
    parser.add_argument("--set-gemini-key", help="Set Gemini API key in environment for this session")
    parser.add_argument("--show-gemini-key", action="store_true", help="Show if Gemini API key is set")
    args = parser.parse_args()

    # Handle setting Gemini key
    if args.set_gemini_key:
        os.environ["GEMINI_API_KEY"] = args.set_gemini_key
        print("Gemini API key set in environment for this session.")
        sys.exit(0)

    # Handle showing Gemini key
    if args.show_gemini_key:
        key = os.getenv("GEMINI_API_KEY")
        if key:
            masked = key[:4] + "..." + key[-4:]
            print(f"GEMINI_API_KEY is set: {masked}")
        else:
            print("No Gemini API key set.")
        sys.exit(0)

    # Configure Gemini
    model, temperature = configure_gemini(args.model, args.temp)

    print(colorize("🤖 CLI Genius (Gemini Assistant)", "blue"))
    print("Type your question, use triple quotes for multi-line, '!cmd' for shell, or 'exit' to quit.\n")

    history = []  # conversation context

    while True:
        try:
            user_input = input(colorize("You> ", "yellow")).strip()
            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit"}:
                print(colorize("Goodbye 👋", "red"))
                break

            # Multi-line input
            if user_input.startswith('"""'):
                lines = []
                while True:
                    line = input()
                    if line.strip().endswith('"""'):
                        lines.append(line.strip().rstrip('"""'))
                        break
                    lines.append(line)
                user_input = "\n".join(lines)

            # Shell command integration
            if user_input.startswith("!"):
                output = run_shell_command(user_input[1:])
                print(colorize(f"\n$ {user_input[1:]}\n{output}\n", "green"))
                continue

            # Query Gemini
            response = model.generate_content(
                user_input,
                generation_config={"temperature": temperature}
            )
            reply = response.text.strip()

            print(colorize("\nGemini> ", "green") + reply + "\n")

            # Save to history + log
            history.append({"role": "user", "content": user_input})
            history.append({"role": "model", "content": reply})
            log_interaction(user_input, reply)

        except KeyboardInterrupt:
            print("\nInterrupted. Exiting.")
            break
        except Exception as e:
            print(colorize(f"Error: {e}", "red"))
            break

if __name__ == "__main__":
    main()
