import re

def extract_code(response_text: str) -> str:
    """
    Extracts the content inside <code>...</code> tags.
    """
    match = re.search(r"<code>([\s\S]*?)</code>", response_text)
    if match:
        return match.group(1).strip()
    return ""  # fallback if no code block found

# Example usage
response = "<think>reasoning...</think><code>def reverse_string(s):\n    return s[::-1]</code>"
print(extract_code(response))
