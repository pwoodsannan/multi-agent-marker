# Multi-Agent Marker (WIP)

A multi-agent system that tests how three LLMs assess their own and each other's work. Each agent answers the same question, then marks every answer (including its own) so you can see how the agents rank each other and whether an agent will admit another LLM answered better than it did.

Built with LangGraph, using free open models via OpenRouter.

## How it works

1. **Answer** — three agents (each a *different* open model) independently answer the same question.
2. **Mark** — each agent then scores every answer: its own *and* the other two. Marker identities are shown, so an agent knows which answer is its own.
3. **Rank** — the scores are aggregated to show how the agents rank each other, and where each answer lands overall.

** Question**  "Can you capture and write the feeling of nostalgia in 200 words or less"
## What it measures

- **How the agents rank each other** — the overall ordering once all marks are combined.
- **Self-assessment** — whether an agent rates another agent's answer above its own. If Agent 1 marks Agent 2's answer higher than its own, that's captured directly.
- The gap between an agent's self-score and the scores its answer receives from the others.

## Requirements

- Python 3.x
- An OpenRouter API key (free tier works)

## Setup

1. Clone the repo and enter the folder.
2. Create and activate a virtual environment:

   ```
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your OpenRouter key:

   ```
   OPENROUTER_API_KEY=your_key_here
   ```

## Running it

```
python main.py
```

## Configuration

The three model IDs live in [ .env / config — confirm which you used ] so a dead free model is a one-line swap.

Current models:
- [ model 1 ID ]
- [ model 2 ID ]
- [ model 3 ID ]

## Notes

- Free OpenRouter models are rate-limited (roughly 50 requests/day on an unfunded account). A full run is 3 answers + 9 markings, so watch the daily cap.
- Free models rotate out without warning — keep IDs in config, not hard-coded.





