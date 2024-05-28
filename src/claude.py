import anthropic
import base64
import httpx

image_path = "/Users/saenns/counter-cat/data/cat on counter.jpg"
# image_path = "/Users/saenns/counter-cat/data/cat on floor.jpg"
# image_path = "/Users/saenns/counter-cat/data/cat on counter near.jpg"
# image_path = "/Users/saenns/counter-cat/data/no cats.jpg"
image1_url = f"file://{image_path}"
image1_media_type = "image/jpeg"
with open(image_path, "rb") as f:
	image1_data = base64.b64encode(f.read()).decode("utf-8")

client = anthropic.Anthropic(
    api_key="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",
)
message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    # system="Answer questions about the image in json", # <-- system prompt
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image1_media_type,
                        "data": image1_data,
                    },
                },
                {
                    "type": "text",
                    "text": "Are there any cats on the countertops or tabletops in this image?  Please answer with a single word: yes or no"
                }
            ],
        }
    ],
)
print(message)

