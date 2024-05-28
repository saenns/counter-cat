from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import RPi.GPIO as GPIO
import json
import logging

class WebRequestHandler(BaseHTTPRequestHandler):

    def blow_horn(self, message, secs):
        GPIO.output(pin, 1)
        time.sleep(secs)
        GPIO.output(pin, 0)
        self.time_of_last_honk = time.time()

    def do_GET(self):
            self.blow_horn(message, 0.1)

    def do_POST(self):
        self.do_GET()

if __name__ == "__main__":
    logging.basicConfig(level='INFO', format='%(asctime)s %(message)s')
    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
    server.serve_forever()
