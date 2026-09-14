"""HTTP service for Counter Cat."""

from __future__ import annotations

import base64
import json
import logging
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import ClassVar

from .classifier import CounterClassifier

LOG = logging.getLogger(__name__)
MAX_IMAGE_BYTES = 10 * 1024 * 1024


class Alarm:
    """Optional Raspberry Pi GPIO alarm; safely degrades off a Pi."""

    def __init__(self, pin: int | None, seconds: float) -> None:
        self.seconds = seconds
        self.gpio = None
        if pin is None:
            return
        try:
            import RPi.GPIO as gpio
        except ImportError:
            LOG.warning("RPi.GPIO is unavailable; alarm is disabled")
            return
        gpio.setmode(gpio.BCM)
        gpio.setup(pin, gpio.OUT, initial=gpio.LOW)
        self.gpio = gpio
        self.pin = pin

    def sound(self) -> None:
        if self.gpio is None:
            return
        self.gpio.output(self.pin, self.gpio.HIGH)
        try:
            import time

            time.sleep(self.seconds)
        finally:
            self.gpio.output(self.pin, self.gpio.LOW)


class CounterCatHandler(BaseHTTPRequestHandler):
    classifier: ClassVar[CounterClassifier]
    alarm: ClassVar[Alarm]

    def do_GET(self) -> None:
        if self.path != "/healthz":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self._reply(HTTPStatus.OK, {"status": "ok"})

    def do_POST(self) -> None:
        if self.path != "/classify":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if not 0 < content_length <= MAX_IMAGE_BYTES * 2:
                raise ValueError("request body must contain one image under 10 MiB")
            payload = json.loads(self.rfile.read(content_length))
            image = base64.b64decode(payload["image"], validate=True)
            media_type = payload.get("media_type", "image/jpeg")
            if (
                not isinstance(media_type, str)
                or media_type not in {"image/jpeg", "image/png"}
                or len(image) > MAX_IMAGE_BYTES
            ):
                raise ValueError("unsupported image or image is too large")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            self._reply(HTTPStatus.BAD_REQUEST, {"error": str(error)})
            return

        try:
            on_counter = self.classifier.classify(image, media_type)
        except Exception:
            LOG.exception("classification failed")
            self._reply(HTTPStatus.BAD_GATEWAY, {"error": "classification failed"})
            return
        if on_counter:
            self.alarm.sound()
        self._reply(HTTPStatus.OK, {"cat_on_counter": on_counter})

    def _reply(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        LOG.info("%s - %s", self.address_string(), fmt % args)


def main() -> None:
    logging.basicConfig(level=os.getenv("COUNTER_CAT_LOG_LEVEL", "INFO"))
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY must be set")
    model = os.getenv("COUNTER_CAT_MODEL", "claude-3-5-sonnet-latest")
    pin = os.getenv("COUNTER_CAT_GPIO_PIN")
    try:
        import anthropic
    except ImportError as error:
        raise SystemExit("Install the package with `pip install .` before starting Counter Cat") from error
    CounterCatHandler.classifier = CounterClassifier(anthropic.Anthropic(api_key=api_key), model)
    CounterCatHandler.alarm = Alarm(int(pin) if pin else None, float(os.getenv("COUNTER_CAT_HONK_SECONDS", "0.2")))
    host = os.getenv("COUNTER_CAT_HOST", "127.0.0.1")
    port = int(os.getenv("COUNTER_CAT_PORT", "8000"))
    LOG.info("starting Counter Cat on %s:%s", host, port)
    ThreadingHTTPServer((host, port), CounterCatHandler).serve_forever()


if __name__ == "__main__":
    main()
