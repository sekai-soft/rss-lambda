import ollama
import base64

with open("3.jpeg", "rb") as f:
    encoded_image = base64.b64encode(f.read())

response = ollama.generate(
    model='llava',
    prompt='Is there a human in this image? If yes, do they show male or female characteristics? Return only in valid JSON string with one JSON key "result" and value being either "no", "male" or "female".',
    images=[encoded_image]
)
print(response['response'])
