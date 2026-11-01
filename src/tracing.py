"""Record how long each step of an answer takes, and what it used."""
import time
from contextlib import contextmanager


class Trace:
    def __init__(self):
        self.spans = []

    @contextmanager
    def span(self, name, **details):
        """Time the code inside a `with` block and save it as one span."""
        record = {"name": name, **details}
        start = time.perf_counter()
        try:
            yield record  # the `with` block runs here, and can add to record
        finally:
            record["seconds"] = round(time.perf_counter() - start, 3)
            self.spans.append(record)

    def summary(self):
        """Calls and total seconds per step name."""
        totals = {}
        for span in self.spans:
            step = totals.setdefault(
                span["name"], {"calls": 0, "seconds": 0.0})
            step["calls"] += 1
            step["seconds"] = round(step["seconds"] + span["seconds"], 3)
        return totals


if __name__ == "__main__":
    trace = Trace()
    with trace.span("claude") as span:
        time.sleep(0.2)
        span["input_tokens"] = 100
    with trace.span("search", query="first"):
        time.sleep(0.1)
    with trace.span("search", query="second"):
        time.sleep(0.1)
    try:
        with trace.span("search", query="broken"):
            raise ValueError("search failed")
    except ValueError:
        pass
    print(trace.spans)
    print(trace.summary())
