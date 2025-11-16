import re

def extract_code(response_text: str) -> str:
    """
    Extracts the content inside triple backticks ``` ... ```
    """
    match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", response_text)
    if match:
        return match.group(1).strip()
    return ""  # fallback if no code block found

# # Example usage
# response = """<think>reasoning...</think>

# ```python
# def reverse_string(s):
#     return s[::-1]
# ```"""

# print(extract_code(response))
