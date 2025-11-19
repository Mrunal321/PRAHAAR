1. What is our main work?

PRAHAAR is essentially:

“Prescriptive Reconstruction of Attacks and Holistic analysis of Alerts via Agentic-AI for Robust Cybersecurity… using an offensive (Red) agent and a defensive (Blue) agent, evaluated via Red vs Blue interaction.”

Concretely, your main contributions should be:

Design and implement a Red Agent (offensive) in a controlled lab setup

Start with phishing mail generator (Milestone 1).

Later maybe extend to simple fuzzing/probing of a test web app or service.

This must be for simulation / training, not for attacking real systems.

Design and implement a Blue Agent (defensive)

It receives alerts/logs/emails and:

classifies them (phishing vs benign),

reconstructs a simple “attack story”,

suggests responses (block, warn user, etc.).

Red vs Blue evaluation loop

Run controlled experiments:

Red generates attacks (e.g., phishing examples),

Blue tries to detect / explain / respond.

Measure: detection rate, false positives, response quality, etc.

This “closed loop” is your core result, not raw code dumps.

Tie to existing work

Use ideas from:

Automatic LLM Red Teaming,

LLM-guided fuzzing,

LLM-based phishing education,

but at a smaller, implementable scale for your course/project.

That’s it. If you try to fully reproduce all those USENIX/NDSS papers, you will drown.

2. How and where should you start?

Right now your slides show:

Step 1: Agentic AI basics – done

Step 2: Learning Python – ongoing

Step 3: Finding and fine-tuning code – done (sort of)

Step 4: VM + sandbox – in progress

You’re stuck in the “looking at GitHub + nothing works” loop. You need a minimal, self-contained pipeline that you control.

Phase 0 – Narrow the scope (today)

Decide a very tight scenario:

“Simulated corporate/military email system; Red Agent generates training phishing emails; Blue Agent classifies them and explains why they’re dangerous.”

Forget fuzzers, protocol fuzzing, and full OS hacking for now. Those papers are inspiration, not deliverables.

Phase 1 – Minimal Red Agent (Milestone 1, but realistic)

Goal: One Python script that can:

Take a scenario (e.g., “salary slip”, “IT support”, “account verification”).

Call an LLM API.

Get back a simulated phishing email example marked as for training/education.

Architecturally:

agent.py

Decides: “I want a phishing example for scenario X.”

Calls a tool.

tools/phishing_generator.py

Has a function like generate_phishing_example(scenario, difficulty_level)

Internally calls LLM with a safe prompt, e.g.:

“Generate a realistic-looking email that could be used in phishing, but clearly mark the red flags and include a warning line at the top that this is for training purposes.”

You do not need a fancy agent framework first (LangChain / AutoGen / etc.). Start with plain Python + a single API call.

Deliverable for Phase 1:

A CSV/JSON of, say, 100 generated emails with labels: scenario, difficulty, and the text.

A short script to view a few examples.

Phase 2 – Minimal Blue Agent

Goal: Another script that:

Reads those emails (from CSV/JSON).

For each email, asks an LLM:

“Is this email likely phishing or benign in a training dataset?”

“Explain in 2–3 bullet points what the warning signs are.”

It then:

Stores prediction + explanation.

Compares prediction with the ground truth label (you know all generated ones are “phishing”, and you can also create some benign emails for balance).

Deliverables:

Basic metrics: accuracy, precision/recall, confusion matrix.

Sample explanations.

Phase 3 – Simple Red vs Blue “game”

Now wrap Phase 1 + 2 into a loop:

Red Agent picks a scenario and difficulty.

Generates N emails.

Blue Agent evaluates them.

Log:

how many it caught,

which ones it missed,

which explanations were weak.

Optionally:

Let Red “adapt”: if Blue keeps catching a pattern, Red can change scenario template (still within safe, training context).

This gives you experiments and graphs. That’s what the paper/report needs.

Phase 4 – Decide how far to go

If time allows:

Extend inputs:

Phishing SMS samples.

Simulated login pages (pure HTML in a lab environment).

Extend Blue Agent:

Analyses simple “logs” from a dummy mail server (timestamps, IP countries, etc.).

Reconstructs a simple attack sequence:

“Step 1: Phishing mail sent; Step 2: link clicked; Step 3: credentials posted”.

But don’t touch real systems, real credentials, or real production infra. Keep it toy but coherent.

3. What will you need?
Skills

Realistically, you need:

Solid basic Python

Functions, classes, modules, virtualenv.

requests or official API library usage.

Reading/writing JSON/CSV.

Basic “agentic” concepts

An “agent” is just:

a loop,

a state,

a set of tools (functions),

and an LLM call for planning.

Very light ML/eval

How to compute accuracy, confusion matrix.

How to design a simple experiment.

You don’t need:

Deep RL training from scratch,

Custom transformers,

Full fuzzing engine like AFL integrated with everything.

Tools / Infra

One VM (Linux) – sandboxed:

Python 3.10+,

virtualenv or conda,

git.

One LLM API (whatever your institute/legal access permits)

Make sure:

It allows your educational “phishing training” use case.

You obey ToS and ethical constraints.

Simple storage/processing

CSV/JSON files for datasets.

Optionally a tiny SQLite DB or just plain files.

Visualization

Python + matplotlib or just export to CSV and use Excel/LibreOffice for graphs.

Reading Material
