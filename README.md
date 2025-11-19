# PRAHAAR – Red/Blue Agent Playground

This repository collects everything for the PRAHAAR project: data, code, documentation, and experiment assets. The focus is a safe, self-contained red-vs-blue loop for phishing-email simulations.

## Repository layout

- `docs/` – background notes such as `project_brief.md` (the original plan you pasted from ChatGPT).
- `src/` – Python packages.
  - `red_agent/` – phishing generation logic.
  - `blue_agent/` – classification/evaluation logic.
  - `common/` – helpers shared by both agents (LLM client, config, metrics).
- `data/` – generated datasets (`raw/`) and cleaned/annotated versions (`processed/`).
- `scripts/` – CLI utilities (dataset generation, evaluation loop, etc.).

## Suggested first steps

1. **Set up the environment**
   - `python3 -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`
   - Add an `.env` file with your API key (e.g., `OPENAI_API_KEY=...`).

2. **Implement the minimal Red Agent**
   - Fill in `src/common/llm_client.py` (basic wrapper around your LLM API).
   - Implement `src/red_agent/scenarios.py` with a small catalog of phishing scenarios.
   - Implement `src/red_agent/generator.py` with a `generate_phishing_example` function that:
     1. Accepts `scenario`, `difficulty`, and safety toggles.
     2. Calls the shared LLM client with a safe prompt.
     3. Returns structured data (`dict` with `scenario`, `difficulty`, `body`, `red_flags`).
   - Create `scripts/generate_dataset.py` to loop over scenarios/difficulties and save JSON/CSV in `data/raw/`.

3. **Ship the minimal Blue Agent**
   - Add `src/blue_agent/classifier.py` that loads a dataset entry, asks the LLM for phishing/benign + explanation, and returns predictions.
   - Write `scripts/evaluate_blue_agent.py` that consumes the generated dataset and prints accuracy/precision/recall.

4. **Close the loop**
   - Add `scripts/run_simulation.py` that ties Red + Blue together in one run, logs misses, and dumps metrics for later visualization.

All new code should live under `src/` and import via the package path (e.g., `from red_agent.generator import ...`). Keep documentation in `docs/`, generated artifacts in `data/`, and automation scripts under `scripts/`.

## Next actions checklist

- [ ] Create `.env.example` listing required environment variables.
- [ ] Implement `src/common/llm_client.py` (even if it initially uses a dummy template instead of a real API call).
- [ ] Build `scripts/generate_dataset.py` and store the first CSV in `data/raw/`.
- [ ] Draft a `scripts/evaluate_blue_agent.py` skeleton with placeholder evaluation metrics.
- [ ] Record observations/metrics under `docs/experiments/` as you run simulations.

Once these boxes are checked you will have the backbone needed to iterate on smarter agents, add metrics, and write up the experimental results.
