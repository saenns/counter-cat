import anthropic
import base64
import time
import glob
import httpx



image_path = "/Users/saenns/counter-cat/data/positive/cat on counter.jpg"
# image_path = "/Users/saenns/counter-cat/data/cat on floor.jpg"
# image_path = "/Users/saenns/counter-cat/data/cat on counter near.jpg"
# image_path = "/Users/saenns/counter-cat/data/no cats.jpg"

client = anthropic.Anthropic(
    api_key="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",
)

for image_path in glob.glob('/Users/saenns/counter-cat/data/negative/*.jpg'):
    start_time = time.perf_counter()
    print(image_path)
    with open(image_path, "rb") as f:
        image1_data = base64.b64encode(f.read()).decode("utf-8")
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
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
                            "media_type":  "image/jpeg",
                            "data": image1_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Are there any cats on the countertops or tabletops in this image? Remember that cabinets are not countertops.  Answer no if there are cats on top of the cabinets but not on the countertops. Otherwise answer yes. Please answer with a single word: yes or no"
                    }
                ],
            }
        ],
    )
    end_time = time.perf_counter()
    print(message)
    print(message.content[0].text)
    print(f'{end_time - start_time} seconds')

