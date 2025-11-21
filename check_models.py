import google.generativeai as genai

# Paste your Gemini API key here temporarily (or use dotenv if you prefer)
genai.configure(api_key="AIzaSyADi6TH-8ltfAKVVwZrHh73IPxUQT3IgK0")

print("\n🧠 Listing available Gemini models...\n")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)
