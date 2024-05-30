from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import RPi.GPIO as GPIO
import base64
import cv2
import json
import logging
import requests
import time

# OpenAI API Key
def payload(base64_image):
    return {
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

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

class WebRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        cap = cv2.VideoCapture("rtsp://admin:Bsff7NUTWKUf@192.168.1.64:554/Streaming/Channels/101?transportmode=unicast&profile=Profile_1")
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        ret, frame = cap.read()
        if not cap.isOpened():
            raise Exception("Error: Could not open RTSP stream")

# Try to grab a frame
        ret, frame = cap.read()
        if not ret:
            raise Exception("Error: Could not read frame from the stream: " + ret)

        image_path = f'./capture_{time.time()}.jpg'

        cv2.imwrite(image_path, frame)

# jrgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# jimage_pil = Image.fromarray(image_rgb)
# Path to your image
        logging.info(image_path)
# Getting the base64 string
        base64_image = encode_image(image_path)
        api_key = "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"
        headers = {
          "Content-Type": "application/json",
          "Authorization": f"Bearer {api_key}"
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload(base64_image))

        logging.info(response.json())

        content = json.loads(response.json()['choices'][0]['message']['content'])
        if content['answer']:
            logging.info('honking the horn')
            # requests.get("http://airhorn.my:8000/h1")
            GPIO.output(pin, 1)
            time.sleep(secs)
            GPIO.output(pin, 0)
            self.time_of_last_honk = time.time()
        else:
            logging.info('no cats on countertop')
        cap.release()
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
