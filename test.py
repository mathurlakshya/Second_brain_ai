from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

for model in [
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-pro-latest",
    "gemini-3.5-flash",
]:
    print(f"\nTesting: {model}")
    try:
        response = client.models.generate_content(
            model=model,
            contents="Hello"
        )
        print("SUCCESS:", response.text)
        break
    except Exception as e:
        print("FAILED:", e)