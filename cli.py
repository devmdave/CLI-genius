#!/usr/bin/env python3

# AI Commit Assistant CLI (Gemini Edition)
# - Generates commit messages from staged changes.
# - Supports conventional/emoji/plain styles.
# - Offline heuristic summarizer + Gemini LLM summarizer.

# Usage:
#   ./ai_commit.py --set-gemini-key <YOUR_KEY>
#   ./ai_commit.py --show-gemini-key
#   ./ai_commit.py generate -s conventional --dry-run
#   ./ai_commit.py commit -s emoji


import os
import sys
import subprocess
import argparse
import re
from typing import List, Tuple, Optional

# -----------------------------
# Git helpers
# -----------------------------

def run(cmd: List[str]) -> Tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out.strip(), err.strip()

def ensure_git_repo() -> str:
    code, out, err = run(["git", "rev-parse", "--show-toplevel"])
    if code != 0:
        sys.exit("Error: Not inside a Git repository.")
    return out

def get_staged_files() -> List[str]:
    code, out, err = run(["git", "diff", "--cached", "--name-only"])
    if code != 0:
        sys.exit(f"Error reading staged files: {err}")
    return [f for f in out.splitlines() if f.strip()]

def get_staged_diff() -> str:
    code, out, err = run(["git", "diff", "--cached"])
    if code != 0:
        sys.exit(f"Error reading staged diff: {err}")
    return out

def commit(message: str) -> None:
    code, out, err = run(["git", "commit", "-m", message])
    if code != 0:
        sys.exit(f"git commit failed:\n{err}\n\nMessage was:\n{message}")
    print(out)

# -----------------------------
# Offline summarizer
# -----------------------------

def summarize_changes_offline(diff: str, files: List[str]) -> str:
    if not diff.strip():
        return "No changes detected"
    added = diff.count("\n+")
    removed = diff.count("\n-")
    return f"Edited {len(files)} file(s), +{added}/-{removed} lines"

# -----------------------------
# Gemini summarizer
# -----------------------------

def summarize_changes_gemini(diff: str, files: List[str], api_key: str) -> Optional[str]:
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = (
            "You are a commit message assistant. Given a git staged diff, produce a one-sentence commit message.\n"
            "- Be specific and actionable.\n"
            "- Use verbs like add, fix, refactor, improve.\n"
            "- Keep under 72 characters.\n"
            f"Files: {', '.join(files)}\n"
            f"Diff:\n{diff[:8000]}\n"
        )

        resp = model.generate_content(prompt)
        text = resp.text.strip()
        return text.splitlines()[0][:100]
    except Exception:
        return None

# -----------------------------
# Message formatting
# -----------------------------

def format_message(style: str, title: str) -> str:
    if style == "conventional":
        return f"chore: {title}"
    elif style == "emoji":
        return f"🔧 {title}"
    else:
        return title

# -----------------------------
# CLI
# -----------------------------

def generate_message(style: str) -> str:
    ensure_git_repo()
    files = get_staged_files()
    if not files:
        sys.exit("No staged files. Stage changes first: git add <files>")

    diff = get_staged_diff()
    if not diff.strip():
        sys.exit("Empty staged diff. Did you stage content changes?")

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        summary = summarize_changes_gemini(diff, files, api_key)
    else:
        summary = None

    title = summary or summarize_changes_offline(diff, files)
    return format_message(style, title)

def main():
    parser = argparse.ArgumentParser(description="AI Commit Assistant CLI (Gemini)")
    parser.add_argument("--set-gemini-key", help="Set Gemini API key in environment")
    parser.add_argument("--show-gemini-key", action="store_true", help="Show if Gemini API key is set")
    sub = parser.add_subparsers(dest="cmd")

    p_gen = sub.add_parser("generate", help="Generate a commit message")
    p_gen.add_argument("-s","--style", choices=["conventional","emoji","plain"], default="conventional")
    p_gen.add_argument("--dry-run", action="store_true")

    p_commit = sub.add_parser("commit", help="Generate and commit")
    p_commit.add_argument("-s","--style", choices=["conventional","emoji","plain"], default="conventional")
    p_commit.add_argument("--dry-run", action="store_true")

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

    if args.cmd not in ("generate","commit"):
        parser.print_help()
        sys.exit(1)

    message = generate_message(style=args.style)

    if args.dry_run or args.cmd == "generate":
        print("\n--- Commit message (preview) ---\n")
        print(message)
        print("\n-------------------------------\n")
        return

    commit(message)

if __name__ == "__main__":
    main()
