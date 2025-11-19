Phase 0 – Project setup (done)

Organize repo (docs, src, data, scripts), add README, requirements, .env.
Implement shared config + OpenAI client.
Phase 1 – Red agent baseline (done)

Define phishing scenarios + prompt template.
Generate small CSVs (per-scenario N) using scripts/generate_dataset.py.
Phase 2 – Blue agent baseline (done)

Write classifier that reads each email, asks LLM for phishing|benign, and logs reasons.
Run scripts/evaluate_blue_agent.py against the generated dataset.
Phase 3 – Closed-loop simulation (done)

Combine Red + Blue into scripts/run_simulation.py to log CAUGHT/MISSED results.
Phase 4 – Enrich inputs & realism (next)

Add benign email generator/templates with label=benign to measure false positives.
Capture extra metadata (sender, domain, attachment name, link host) in each sample.
Let Red vary tactics (e.g., real-looking domains, personalized details) using scenario configs.
Phase 5 – Improve Blue defenses

Extend prompt to consider metadata fields; add heuristics (domain allowlists, suspicious attachment filter).
Track precision/recall/confusion matrix; output to JSON/CSV for plotting.
Optionally fine-tune prompts per scenario or add simple rule-based filters before LLM call.
Phase 6 – Experimentation & reporting

Automate batch runs (vary scenario mix, difficulty, model) and store results in docs/experiments/<date>.md.
Plot metrics (matplotlib or notebook) to show detection vs. difficulty, false positives, etc.
Document limitations (text-only signals, API cost, latency) and potential mitigations.
Phase 7 – Optional extensions

Generate phishing SMS or voice scripts, as separate Red modules.
Simulate simple attack chains (phish → link click → fake login) and have Blue reconstruct the timeline.
Introduce adaptive Red agent that reads Blue’s misses and tries new tactics automatically.
