import os
from dotenv import load_dotenv
import google.generativeai as genai
from tavily import TavilyClient

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content("Explain neural networks in 3 bullet points.")

print(response.text)


tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

results = tavily.search("neural networks explained 2024")

for r in results["results"][:3]:
    print(r["title"])
    print(r["url"])
    print()