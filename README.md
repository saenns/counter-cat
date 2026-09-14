# Counter Cat

Counter Cat is a small HTTP service for a Raspberry Pi camera setup: send it a
JPEG or PNG snapshot and it determines whether a cat is on a countertop or
tabletop. When configured with GPIO, a positive result briefly activates an
alarm.

It is intentionally a personal-project reference implementation, not a
security-hardened camera system. It sends submitted images to Anthropic for
classification; deploy it only on a trusted network and with the consent of
people who may appear in the camera view.

## What it does

`POST /classify` accepts a JSON body containing a base64-encoded image and
returns a simple result:

```json
{"cat_on_counter": true}
```

`GET /healthz` returns `{"status": "ok"}` for service monitoring. Images are
not written to disk by the application.

## Setup

Counter Cat requires Python 3.10+ and an [Anthropic API key](https://console.anthropic.com/).
On Raspberry Pi OS, install the GPIO extra; on a development machine, omit it.

```sh
git clone https://github.com/saenns/counter-cat.git
cd counter-cat
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[gpio]'
cp .env.example .env
```

Set `ANTHROPIC_API_KEY` in your environment (or source your local `.env` with
your preferred secret-management tool), then start the service:

```sh
export ANTHROPIC_API_KEY='…'
counter-cat
```

The default listener is `127.0.0.1:8000`; use a reverse proxy or explicitly set
`COUNTER_CAT_HOST` if another machine must reach it.

## Request example

```sh
IMAGE_B64=$(base64 < snapshot.jpg | tr -d '\n')
curl -X POST http://127.0.0.1:8000/classify \
  -H 'Content-Type: application/json' \
  --data "{\"image\":\"$IMAGE_B64\",\"media_type\":\"image/jpeg\"}"
```

The maximum decoded image size is 10 MiB. JPEG and PNG are supported.

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | — | Required API credential. Never commit it. |
| `COUNTER_CAT_MODEL` | `claude-3-5-sonnet-latest` | Anthropic vision model to use. |
| `COUNTER_CAT_HOST` | `127.0.0.1` | HTTP bind address. |
| `COUNTER_CAT_PORT` | `8000` | HTTP port. |
| `COUNTER_CAT_GPIO_PIN` | unset | BCM GPIO pin to activate on a positive result. |
| `COUNTER_CAT_HONK_SECONDS` | `0.2` | Alarm duration in seconds. |

## Raspberry Pi service

Install the package into a dedicated virtual environment, update the paths and
user in [`countercat.service`](etc/systemd/system/countercat.service), and copy
it to `/etc/systemd/system/`. Store the API key in a root-readable environment
file such as `/etc/counter-cat.env` (mode `600`), then enable the unit:

```sh
sudo systemctl daemon-reload
sudo systemctl enable --now countercat
sudo systemctl status countercat
```

## Development

```sh
pip install -e '.[dev]'
ruff check .
pytest
```

The former local camera captures are deliberately not part of the runtime or
test suite. Keep any private captures outside Git; the `captures/` directory is
ignored for that purpose.

## Security note

An API key that appeared in an earlier revision of this repository must be
revoked and replaced. Removing it from the current source does not remove it
from Git history or invalidate the credential.

## License

[MIT](LICENSE)
