"""
Simple script to call OpenAI endpoint with Langfuse observability
Uses Langfuse's OpenAI wrapper for automatic tracing
Loads prompt from Langfuse Prompt Management
"""

import os
from dotenv import load_dotenv
from langfuse.openai import openai
from langfuse import get_client

# Load environment variables
load_dotenv()

# Initialize Langfuse client
langfuse = get_client()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load prompt from Langfuse Prompt Management
prompt = langfuse.get_prompt("research_assistant_system_prompt")

# Get prompt text and config
prompt_text = prompt.prompt
model = prompt.config.get("model", "gpt-3.5-turbo") if prompt.config else "gpt-3.5-turbo"
temperature = prompt.config.get("temperature", 0.7) if prompt.config else 0.7

# Call OpenAI with automatic tracing
result = openai.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": prompt_text},
        {"role": "user", "content": "What are the key characteristics of Baroque music?"}
    ],
    temperature=temperature,
)

# Print result
print("=" * 60)
print("OpenAI Response:")
print("=" * 60)
print(result.choices[0].message.content)
print("=" * 60)

# Flush to send trace immediately
langfuse.flush()

print("\n✅ Trace sent to Langfuse! Check dashboard in 2-5 seconds.")
print("   Visit: https://cloud.langfuse.com")

