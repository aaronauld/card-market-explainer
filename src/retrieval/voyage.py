"""Turn text into embeddings with the Voyage AI REST API."""
import json
import urllib.error
import urllib.request
import time

URL = "https://api.voyageai.com/v1/embeddings"
MODEL = "voyage-4"
DIMENSIONS = 1024     # must match vector(1024) in the chunks table
BATCH_SIZE = 128      # texts per request


def embed(texts, input_type, api_key):
    """Return one vector per text, in the same order.
    input_type is 'document' for chunks or 'query' for questions."""
    vectors = []
    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]
        body = json.dumps({
            "input": batch,
            "model": MODEL,
            "input_type": input_type,
            "output_dimension": DIMENSIONS,
            "truncation": False,
        }).encode("utf-8")
        request = urllib.request.Request(URL, data=body, method="POST", headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        })
        for attempt in range(5):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    result = json.load(response)
                break
            except urllib.error.HTTPError as err:
                if err.code == 429 and attempt < 4:
                    time.sleep(21)  # free tier: 3 requests per minute
                    continue
                message = err.read().decode("utf-8")
                raise RuntimeError(
                    f"Voyage API error {err.code}: {message}") from err

        items = sorted(result["data"], key=lambda item: item["index"])
        vectors.extend(item["embedding"] for item in items)
    return vectors
