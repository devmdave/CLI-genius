import re
import time
import os
from rich.console import Console
from rich.text import Text


# Create a console object
console = Console()


def extract_code(response_text: str) -> str:
    """
    Extracts the content inside triple backticks ``` ... ```
    """
    match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", response_text)
    if match:
        return match.group(1).strip()
    return ""  # fallback if no code block found


def generate_filename_from_prompt(prompt: str, extension: str = ".py") -> str:
    """
    Generate a safe filename from a natural language prompt.
    """
    # Extract words (alphanumeric only)
    words = re.findall(r"[a-zA-Z0-9]+", prompt)
    if not words:
        return f"generated_{int(time.time())}{extension}"
    
    # Take first 3-5 keywords for brevity
    keywords = "_".join(words[:5]).lower()
    
    return f"{keywords}{extension}"



def save_code_interactive(code: str, filename: str) -> None:
    """
    Ask the user if they want to create a file and save the provided code.
    
    Args:
        code (str): The code to be written into the file.
        filename (str): The name of the file to create/write.
    """
    console.input(f"[bold green]Do you want to create a file named '{filename}'? (y/n):[/bold green] ")
    choice = console.input(f"[bold green]Do you want to create a file named '{filename}'? (y/n):[/bold green] ").strip().lower()
    if choice == "y":
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        console.print(f"✅ Code saved to {filename} successfully!", style="green")

    else:
        console.print("❌ Cannot Save code to File.", style="bold red")



def detect_extension(prompt: str) -> str:
    """
    Detects file extension from the prompt. 
    If not found, checks files in the current working directory and returns the extension.
    Defaults to '.txt' if nothing is found.
    """
    # Map common language keywords to extensions
    lang_map = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "java": ".java",
        "cpp": ".cpp",
        "c++": ".cpp",
        "c": ".c",
        "go": ".go",
        "rust": ".rs",
        "html": ".html",
        "css": ".css",
        "bash": ".sh",
        "shell": ".sh",
        "php": ".php",
        "ruby": ".rb",
    }

    # Try to detect from prompt
    for lang, ext in lang_map.items():
        if re.search(rf"\b{lang}\b", prompt.lower()):
            return ext

    # If not found, check current directory files
    for file in os.listdir("."):
        _, ext = os.path.splitext(file)
        if ext:  # return first valid extension
            return ext

    # Fallback
    return ".txt"