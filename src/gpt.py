import base64
import requests

# OpenAI API Key
api_key = "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"

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
images = [
# "/Users/saenns/counter-cat/data/cat on counter.jpg",
# "/Users/saenns/counter-cat/data/cat on floor.jpg",
# "/Users/saenns/counter-cat/data/cat on counter near.jpg",
# "/Users/saenns/counter-cat/data/no cats.jpg",
# "/Users/saenns/counter-cat/data/miso front center.jpg",
# "/Users/saenns/counter-cat/data/miso partially obscure.jpg",
# "/Users/saenns/counter-cat/data/miso far.jpg",
# "/Users/saenns/counter-cat/data/miso on edge.jpg",
"/Users/saenns/counter-cat/data/oliver front center.jpg"]

for image_path in images:
    print(image_path + '\n')
# Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
    }

    payload = {
      "model": "gpt-4o",
      "response_format": { "type": "json_object" },
      "messages": [
        {
          "role": "system",
          "content": [
            {
              "type": "text",
              "text": "You are an image analyzer.  You answer questions about the image with true or false in a json object with a boolean field called 'answer'."
            }
          ]
        },
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "Are there any cats on the countertops or tabletops in this image?"
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json())

