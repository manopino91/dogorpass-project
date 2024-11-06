import google.generativeai as genai

# Configure the API key directly
genai.configure(api_key='AIzaSyB7XmXme-EP4bDpmmp6dlAGIBmGzY0m6iY')

# Check and print available models
models = genai.list_models()
print("Available Gemini Models:")
for model in models:
    print(model)
