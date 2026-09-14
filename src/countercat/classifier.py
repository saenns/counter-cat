"""Image classification through Anthropic's vision API."""

from __future__ import annotations

import base64
import re

PROMPT = (
    "Is a cat on a countertop or tabletop in this image? Cabinets, window sills, "
    "chairs, and floors do not count. Reply with exactly YES or NO."
)


def is_affirmative(response: str) -> bool:
    """Interpret the deliberately constrained model reply defensively."""
    return bool(re.match(r"^\s*yes\b", response, flags=re.IGNORECASE))


class CounterClassifier:
    """Classify a JPEG or PNG image without retaining it locally."""

    def __init__(self, client: object, model: str) -> None:
        self.client = client
        self.model = model

    def classify(self, image: bytes, media_type: str) -> bool:
        encoded_image = base64.b64encode(image).decode("ascii")
        message = self.client.messages.create(
            model=self.model,
            max_tokens=3,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": encoded_image,
                            },
                        },
                        {"type": "text", "text": PROMPT},
                    ],
                }
            ],
        )
        return is_affirmative(message.content[0].text)
