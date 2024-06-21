from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import RPi.GPIO as GPIO
import base64
#import cv2
import json
import logging
# import requests
import time
import anthropic

pin = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)

client = anthropic.Anthropic(
    api_key="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",
)

class WebRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        image_path = f'./capture_{time.time()}.jpg'
        logging.info(image_path)
        content_len = int(self.headers.get('Content-Length'))
        request_body = json.loads(self.rfile.read(content_len))

        # logging.info(f'request_body: {request_body}')

        base64_image = request_body['image']
        # logging.info(f'base64_image: {base64_image}')
        with open(image_path, 'wb') as imgf:
            imgf.write(base64.b64decode(base64_image))

        logging.info(image_path)

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
                                "data": base64_image,
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

        logging.info(f'{message}')

        # content = json.loads(response.json()['choices'][0]['message']['content'])
        if message.content[0].text == 'Yes':
            logging.info('honking the horn')
            GPIO.output(pin, 1)
            time.sleep(0.2)
            GPIO.output(pin, 0)
            self.time_of_last_honk = time.time()
        else:
            logging.info('no cats on countertop')
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'ok')

    def do_POST(self):
        self.do_GET()

if __name__ == "__main__":
    logging.basicConfig(level='INFO', format='%(asctime)s %(message)s')
    logging.info('test')
    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
    server.serve_forever()
