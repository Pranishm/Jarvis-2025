import google.generativeai as genai

# Replace with your actual API key
genai.configure(api_key="AIzaSyAzW7zdxVYWB0UaGCm19eY_VT1JRYh5dw8")

model = genai.GenerativeModel('gemini-1.5-pro')

def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text
