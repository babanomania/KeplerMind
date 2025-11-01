### Project: *KeplerMind — Discover · Reflect · Illuminate*

> **Goal:** Build a self-reflective CLI learning companion powered by MCP (Memory · Control · Planning).
> The user gives a topic → the agent performs research → builds a RAG → plans 5 adaptive questions → evaluates and reflects → explains → commits durable memories.

---

## 🌌 Phase 0 — Repository Setup

**Objective:** Bootstrap CLI environment and core layout.

* [ ] Create folder structure:

  ```
  keplermind/
    app/
      nodes/
      mcp/
      tools/
      prompts/
      config/
      memory/
    assets/outputs/
    tests/
  ```
* [ ] Add `requirements.txt` with:

  ```
  langchain
  langgraph
  chromadb
  duckduckgo-search
  openai
  readability-lxml
  requests
  pandas
  numpy
  rich
  python-dotenv
  pydantic>=2
  pytest
  ```
* [ ] Add `.env.example` with:

  ```
  OPENAI_API_KEY=
  TAVILY_API_KEY=
  ```
* [ ] Add `.gitignore`:
  `.env`, `__pycache__`, `assets/outputs/*`, `*.sqlite`, `.DS_Store`
* [ ] Create `Makefile` with targets:

  * `make run`
  * `make test`
  * `make clean`
* [ ] Add placeholder `README.md` (will later describe CLI usage).
* [ ] Create `config/settings.py` with model names, chunk sizes, and time budget constants.

---

## 🧠 Phase 1 — LangGraph Backbone

**Objective:** Implement the brain that orchestrates all nodes.

* [ ] `app/state.py`:
  Define `TypedDict S` (topic, goal, priors, sources, plan, questions, qa, profile, explanations, mem_candidates, artifacts).

* [ ] `app/graph.py`:

  * [ ] Wire all nodes: `intake → research → build_rag → planner → ask_and_score → reflect_and_repair → profile → explain → memorize → report`.
  * [ ] Implement conditional edges: reflection loops and repair checks.
  * [ ] Print rich-style DAG summary in CLI at startup.

* [ ] `app/main.py`:

  * [ ] Implement a single CLI entrypoint using `argparse`.
  * [ ] Options:

    ```
    --topic "Kafka Architecture"
    --goal "prepare for interview"
    --level-hint intermediate
    --time 300
    --style bullet
    ```
  * [ ] Log progress with `rich.console` + timestamps.
  * [ ] On completion: show summary table of scores and output paths.

---

## 🧩 Phase 2 — MCP Core System

**Objective:** Implement memory persistence and planning priors.

* [ ] `mcp/stores.py`:

  * SQLite episodic log (`events(id, ts, session, phase, payload)`).
  * Chroma/FAISS semantic store.
  * JSON preference KV (`preferences.json`).

* [ ] `mcp/policies.py`:

  * scoring/retention formulas.
  * summarization & redaction (truncate >240 chars).
  * top-N class retention logic.

* [ ] `mcp/controller.py`:

  * `propose()`, `review()`, `commit()`, `retrieve()` with scoring weights.
  * Add audit to episodic log.

* [ ] `mcp/priors.py`:

  * Beta priors for per-skill knowledge.
  * Thompson sampling for question planning.
  * spaced repetition schedule generator.

* [ ] Test: `tests/test_mcp_policies.py`.

---

## 🔍 Phase 3 — Research & RAG Pipeline

**Objective:** Let KeplerMind explore, clean, and index the topic.

* [ ] `tools/search.py`: Tavily → fallback to DuckDuckGo.

* [ ] `tools/scrape.py`: HTML → readable text extraction.

* [ ] `nodes/research.py`: orchestrate 8–15 sources, produce `notes[]` + `bibliography.json`.

* [ ] `tools/chunk.py`: chunk text into ~900 tokens, 150 overlap.

* [ ] `tools/embed.py`: embed and store into Chroma.

* [ ] `nodes/build_rag.py`: embed chunks → mark `vector_ready=True`.

* [ ] Prompt: `prompts/hallucination_guard.md`.

* [ ] Test: `tests/test_rag_and_citations.py`.

---

## 🪐 Phase 4 — Planning and Question Design

**Objective:** Generate 10 candidate questions, pick top 5 with MCP priors.

* [ ] `nodes/planner.py`:

  * Read priors, preferences, time budget.
  * Run Thompson sampling → assign difficulty levels.
  * Produce JSON plan with 5-question cap, ≥4 unique skills.
* [ ] Prompts:

  * `prompts/planner.md`
  * `prompts/question_gen.md`
* [ ] Test: `tests/test_planner_priors.py`.

---

## 💬 Phase 5 — Adaptive Q&A Loop

**Objective:** Ask, score, and reflect interactively in CLI.

* [ ] `nodes/ask_and_score.py`:

  * Loop over 5 questions, prompt user for answer + self-confidence (1–5).
  * Grade via `scoring_critic.md`.
  * Update Beta priors + log result.

* [ ] `nodes/reflect_and_repair.py`:

  * Trigger if evidence or score insufficient.
  * Offer minimal repair actions: re-ask, scaffold, lower difficulty.
  * Add `fix_recipe` memory candidate.

* [ ] Prompts:

  * `prompts/scoring_critic.md`
  * `prompts/reflection_critic.md`

* [ ] Test: `tests/test_reflection_loop.py`.

---

## 🧭 Phase 6 — Knowledge Profiling & Explanation

**Objective:** Derive knowledge profile and explain adaptively.

* [ ] `nodes/profile.py`:

  * Aggregate skill gap scores, infer level.
  * Save `profile.json`.

* [ ] `nodes/explain.py`:

  * For low-gap → **light** explanation.
  * For high-gap → **deep** explanation.
  * Add inline citations using `tools/citations.py`.

* [ ] Prompts:

  * `prompts/explain_light.md`
  * `prompts/explain_deep.md`
  * `prompts/cite_merge.md`

* [ ] Test: `tests/test_explain.py`.

---

## 🧠 Phase 7 — Memory Commit & Scheduling

**Objective:** Save durable memories and next review plan.

* [ ] `nodes/memorize.py`:

  * Collect `preference`, `anchor_fact`, `fix_recipe`, `gap_signature`.
  * Call `MemoryController` to score and persist.

* [ ] `nodes/schedule.py`:

  * Compute `next_review.json` using gap/stability ratio.

* [ ] Test: `tests/test_mcp_commit.py`.

---

## 📜 Phase 8 — Reporting & CLI Output

**Objective:** Produce final learning report and summary.

* [ ] `nodes/report.py`:

  * Create `report.md`, `profile.json`, `questions.jsonl`, and `bibliography.json`.
  * Append References list.
  * Print rich summary:

    ```
    Skill        Gap      Level
    Foundations  0.45     Intermediate
    Tools        0.22     Advanced
    Patterns     0.68     Beginner
    ```
  * Display output paths.

* [ ] Test: `tests/test_report.py`.

---

## 💡 Phase 9 — CLI Polish

**Objective:** Make CLI smooth and enjoyable.

* [ ] Add colored sections using `rich` (headers, progress bars, tables).
* [ ] Add “orbit” icon or ASCII logo:

  ```
   ☉  KeplerMind — Discover · Reflect · Illuminate
  ```
* [ ] Graceful fallbacks:

  * If Tavily key missing → DuckDuckGo.
  * If OpenAI key missing → fallback to local embed model (warn).
* [ ] `--quiet` and `--debug` flags.
* [ ] Store all outputs in `assets/outputs/<timestamp>/`.

---

## 🧪 Testing Plan

| File                        | What It Verifies                    |
| --------------------------- | ----------------------------------- |
| `test_mcp_policies.py`      | memory scoring + top-N pruning      |
| `test_rag_and_citations.py` | RAG integrity + citations           |
| `test_planner_priors.py`    | 5-question diversity + priors       |
| `test_reflection_loop.py`   | reflection loop & repair            |
| `test_explain.py`           | adaptive explanations with sources  |
| `test_mcp_commit.py`        | memory commit lifecycle             |
| `test_report.py`            | report completeness & summary table |

Run via:

```bash
pytest -q
```

---

## 🚀 Optional Enhancements

* [ ] **Offline Mode:** cache embeddings + reuse RAG.
* [ ] **Session Resume:** load last profile and continue.
* [ ] **Pretty Graph Print:** ASCII DAG from LangGraph.
* [ ] **Memory Dashboard:** `keplermind memory view` command (prints summary table).

---

## ✨ Completion Criteria

✅ When `python app/main.py --topic "X"` runs end-to-end:

* Web search → RAG build
* MCP planning → 5 Q&A
* Reflection + repair loop
* Profile + explanations generated
* Memory updated
* Final CLI report shown with paths to artifacts