# Demo script (about 3 minutes)

Before recording: start the server and tunnel, and open `/docs` already authorized. Don't show the API key, `.env` or the `.pem` file. The answers show weekly prices, so keep the video private or unlisted until the price data's licence text arrives.

## 1. The problem (20 s)

"Pokémon card prices jump, and the reason is scattered across tournament results, set releases and rotation notices. This system explains why a card moved, using its price history and dated documents, and cites its sources. It explains the past. It doesn't predict prices."

## 2. A live question (60 s)

Send this to `POST /explain`:

```json
{
  "question": "Why did Regidrago VSTAR roughly double in price in early August 2024?",
  "card_id": "swsh12-136",
  "variant": "holo",
  "move_date": "2024-08-04"
}
```

While it runs: "The hard part is that the cause never mentions this card. A new set brought Kyurem, and Regidrago copies Kyurem's attack."

Then show the answer, and read one citation. Point out where it says what the documents don't confirm.

## 3. How it got there (40 s)

Scroll to `tool_calls`: "Claude chose these steps: the prices, then a tournament search, then a search it wrote itself for the set that released Kyurem. Plain RAG, with one search, misses that document."

Scroll to `trace` and `cost_dollars`: "Every step is timed and costed. Most of the time is Claude, and caching cut the cost by about 23%."

## 4. The results (45 s)

Show the README table.

"I measured both pipelines on 28 labelled price moves. The agent has much higher citation and fact recall, and costs about twice as much and is slower. Almost all of the gap is on two-source questions, so if one document is enough, plain RAG is the better choice. It's also a small eval on a corpus I built, so the size of the gap is specific to this data."

Mention one thing that failed: "I tried using retrieval scores to trigger retries. They didn't predict missed documents, so I measured that and removed it."

## 5. Engineering (15 s)

"Retrieval and the agent are hand-written. CI fails if retrieval scores drop, and it runs privately on EC2 behind an SSH tunnel, with an API key and a spending limit."
