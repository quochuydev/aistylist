import json
import logging
import urllib.request

from .config import GEMINI_API_KEY, IMAGE_MODEL


def generate_image(prompt: str):
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGE_MODEL}:predict",
        data=json.dumps({"instances": [{"prompt": prompt}], "parameters": {"sampleCount": 1, "aspectRatio": "3:4"}}).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            img = json.load(r)["predictions"][0]
    except Exception:  # a missing image shouldn't fail the whole run
        logging.exception("image generation failed")
        return None
    # ponytail: inline data URL, no storage; upload to S3 when looks need to persist
    return f"data:{img.get('mimeType', 'image/png')};base64,{img['bytesBase64Encoded']}"
