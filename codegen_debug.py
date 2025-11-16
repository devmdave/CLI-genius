import os
from huggingface_hub import InferenceClient


client = InferenceClient(
    api_key="hf_token",
)

prompt = """You are asked to design a Task Scheduler that manages tasks with priorities, deadlines, and dependencies. The scheduler should determine the optimal order in which tasks should be executed to minimize lateness and respect dependencies.
            Do not include explanations, comments, docstrings, or any text outside the code block. 
            Output must be inside a single <code> ... </code> fenced block /no_think.
"""


completion = client.chat.completions.create(
    model="Qwen/Qwen3-32B:groq",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    
)

print(completion.choices[0].message.content)