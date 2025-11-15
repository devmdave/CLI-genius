#!/usr/bin/env python3
"""
CLI Genius Plus - Extended AI Console Assistant (Gemini Edition)

Fresh Features:
- Persistent config file (~/.cli_genius.json) for defaults (model, temp, key)
- Command shortcuts: /search, /summarize, /translate
- Knowledge mode: /explain <topic> → AI explainer
- Quick notes: /note <text> → saves to notes.log
- History viewer: /history → shows past Q&A
- Gemini key management: --set-gemini-key, --show-gemini-key, --unset-gemini-key
- Colorized output + shell command integration
"""

import os
import sys
import json
import google.generativeai as genai
import subprocess
from datetime import datetime

CONFIG_FILE = os.path.expanduser("~/.cli_genius.json")
LOG_FILE = "cli_genius_plus.log"
NOTES_FILE = "notes.log"

# -----------------------------
# Config Management
# -----------------------------
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"model": "gemini-1.5-flash", "temp": 0.7}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def configure_gemini(model_name: str, temperature: float):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set. Use:\n")
        print("   ./cli_genius_plus.py --set-gemini-key <YOUR_KEY>\n")
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
# Feature Commands
# -----------------------------
def handle_command(cmd: str, model, temperature):
    if cmd.startswith("/note "):
        note = cmd[6:].strip()
        with open(NOTES_FILE, "a") as f:
            f.write(f"[{datetime.now()}] {note}\n")
        return f"📝 Note saved: {note}"

    if cmd.startswith("/history"):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE) as f:
                return f.read()[-1000:]  # show last 1000 chars
        return "No history yet."

    if cmd.startswith("/search "):
        query = cmd[8:].strip()
        response = model.generate_content(f"Search and summarize: {query}")
        return response.text.strip()

    if cmd.startswith("/summarize "):
        text = cmd[11:].strip()
        response = model.generate_content(f"Summarize this text:\n{text}")
        return response.text.strip()

    if cmd.startswith("/translate "):
        parts = cmd.split(" ", 2)
        if len(parts) < 3:
            return "Usage: /translate <lang> <text>"
        lang, text = parts[1], parts[2]
        response = model.generate_content(f"Translate into {lang}:\n{text}")
        return response.text.strip()

    if cmd.startswith("/explain "):
        topic = cmd[9:].strip()
        response = model.generate_content(f"Explain {topic} in simple terms.")
        return response.text.strip()

    return None

# -----------------------------
# Main Loop
# -----------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="CLI Genius Plus - Gemini Assistant")
    parser.add_argument("--model", help="Gemini model (e.g. gemini-1.5-pro)")
    parser.add_argument("--temp", type=float, help="Response creativity (0.0-1.0)")
    parser.add_argument("--set-gemini-key", help="Set Gemini API key in environment for this session")
    parser.add_argument("--show-gemini-key", action="store_true", help="Show if Gemini API key is set")
    parser.add_argument("--unset-gemini-key", action="store_true", help="Unset Gemini API key")
    args = parser.parse_args()

    # Handle key management
    if args.set_gemini_key:
        os.environ["GEMINI_API_KEY"] = args.set_gemini_key
        print("Gemini API key set in environment for this session.")
        sys.exit(0)

    if args.show_gemini_key:
        key = os.getenv("GEMINI_API_KEY")
        if key:
            masked = key[:4] + "..." + key[-4:]
            print(f"GEMINI_API_KEY is set: {masked}")
        else:
            print("No Gemini API key set.")
        sys.exit(0)

    if args.unset_gemini_key:
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
            print("Gemini API key unset.")
        else:
            print("No Gemini API key to unset.")
        sys.exit(0)

    # Load config
    cfg = load_config()
    model_name = args.model or cfg["model"]
    temperature = args.temp if args.temp is not None else cfg["temp"]

    model, temperature = configure_gemini(model_name, temperature)

    print(colorize("🤖 CLI Genius Plus (Gemini Assistant)", "blue"))
    print("Commands: /note, /history, /search, /summarize, /translate, /explain")
    print("Shell: !cmd | Exit: 'exit'\n")

    while True:
        try:
            user_input = input(colorize("You> ", "yellow")).strip()
            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit"}:
                print(colorize("Goodbye 👋", "red"))
                break

            # Shell command integration
            if user_input.startswith("!"):
                output = run_shell_command(user_input[1:])
                print(colorize(f"\n$ {user_input[1:]}\n{output}\n", "green"))
                continue

            # Feature commands
            result = handle_command(user_input, model, temperature)
            if result:
                print(colorize("\nGemini> ", "green") + result + "\n")
                log_interaction(user_input, result)
                continue

            # Default Gemini query
            response = model.generate_content(
                user_input,
                generation_config={"temperature": temperature}
            )
            reply = response.text.strip()
            print(colorize("\nGemini> ", "green") + reply + "\n")
            log_interaction(user_input, reply)

        except KeyboardInterrupt:
            print("\nInterrupted. Exiting.")
            break
        except Exception as e:
            print(colorize(f"Error: {e}", "red"))
            break

if __name__ == "__main__":
    main()
