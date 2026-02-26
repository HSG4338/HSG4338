<div align="center">

```
   _   ___ ___ _  _ _____ ___ ___     _   ___ 
  /_\ / __| __| \| |_   _|_ _/ __|   /_\ |_ _|
 / _ \ (_ | _|| .` | | |  | | (__   / _ \ | | 
/_/ \_\___|___|_|\_| |_| |___\___| /_/ \_\___|
```

**A fully local, agentic AI development system.**  
Give it a goal. It plans, writes code, reviews it, tests it, and commits — no cloud, no paid APIs, just your machine.

<br>

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square&logo=windows)
![Models](https://img.shields.io/badge/Models-HuggingFace%20Local-orange?style=flat-square&logo=huggingface)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Cloud](https://img.shields.io/badge/Cloud-None-red?style=flat-square)

</div>

---

## What it does

You type a goal. A pipeline of AI agents handles the rest:

```
Your goal: "Write a CLI calculator in Python with unit tests"
     │
     ▼
 ┌─────────┐     ┌───────────┐     ┌──────────┐     ┌────────┐     ┌─────────────┐
 │ Planner │ ──► │ Developer │ ──► │ Reviewer │ ──► │   QA   │ ──► │ Repo Manager│
 │         │     │           │     │          │     │        │     │             │
 │Decomposes│    │Writes real│     │APPROVE or│     │Runs    │     │Git commits  │
 │goal into │    │Python files│    │REJECT with│    │pytest  │     │path enforced│
 │task graph│    │to workspace│    │feedback  │     │auto-gen│     │             │
 └─────────┘     └───────────┘     └──────────┘     └────────┘     └─────────────┘
     │                                                                      │
     └──────────────── loops until tests pass or retry limit ───────────────┘
                                       │
                              SQLite memory stores
                         every decision, action & failure
```

Everything runs **100% locally** using small HuggingFace models. No OpenAI. No Anthropic. No internet required after first setup.

---

## Quick Start

### 1. Run the installer
```bat
install_dependencies.bat
```
Creates a virtual environment, installs all dependencies, and pre-downloads the AI model (~2GB, one time only).

### 2. Launch
```bat
run.bat
```
That's it. You'll get an interactive menu:

```
 ╔══════════════════════════════════════╗
 ║  [1]  Submit a goal                  ║  Build something with AI agents
 ║  [2]  Launch web UI                  ║  Dashboard at http://127.0.0.1:5000
 ║  [3]  Run validation                 ║  Check all system components
 ║  [4]  Exit                           ║
 ╚══════════════════════════════════════╝
```

> **First run?** `run.bat` will auto-install dependencies if they're missing — you don't need to run the installer separately.

---

## Requirements

| | |
|---|---|
| **OS** | Windows 10 / 11 |
| **Python** | 3.9 or higher (3.14 tested and working) |
| **RAM** | 4GB minimum — 8GB recommended |
| **Disk** | ~3GB (2GB for model, 1GB for deps) |
| **Internet** | Only needed during first install |

---

## Project Structure

```
agentic_ai/
│
├── agents/                     # The five AI agents
│   ├── planner_agent.py        # Decomposes goals → task graph (never writes code)
│   ├── developer_agent.py      # Writes Python files to /workspace
│   ├── reviewer_agent.py       # Reviews code → APPROVE or REJECT
│   ├── qa_agent.py             # Auto-generates + runs pytest tests
│   └── repo_manager.py         # Git commits, path validation, GitHub push
│
├── orchestrator/
│   └── orchestrator.py         # Goal loop: plan → code → review → test → commit → repeat
│
├── memory/
│   └── memory_store.py         # SQLite: every decision, action, failure logged
│
├── models/
│   └── model_manager.py        # Lazy-load HuggingFace models, in-memory cache
│
├── ui/
│   ├── app.py                  # Flask REST API
│   └── templates/index.html    # Dark web dashboard (no frameworks, vanilla JS)
│
├── tests/                      # Pytest test suite
├── configs/config.json         # All settings: models, thresholds, GitHub
├── cli.py                      # Terminal colours, spinners, boxes, banners
├── main.py                     # CLI entry point
├── run.bat                     # ← Start here on Windows
└── install_dependencies.bat    # One-time setup
```

---

## Configuration

All settings live in `configs/config.json`:

```json
{
  "system": {
    "max_retries": 3,
    "max_goal_iterations": 10,
    "workspace_dir": "workspace"
  },
  "agents": {
    "planner":   { "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "temperature": 0.3 },
    "developer": { "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "temperature": 0.2 },
    "reviewer":  { "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "temperature": 0.1 },
    "qa":        { "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "temperature": 0.1 }
  }
}
```

### Swapping models

Each agent can run a different model. The default is TinyLlama (~2GB) which fits in 4GB RAM.

| Model | Size | Min RAM | Quality |
|---|---|---|---|
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | ~2GB | 4GB | ⭐⭐ |
| `microsoft/phi-2` | ~5GB | 8GB | ⭐⭐⭐ |
| `mistralai/Mistral-7B-Instruct-v0.1` | ~14GB | 16GB | ⭐⭐⭐⭐ |

Just change `model_id` in the config — the model downloads automatically on first use.

---

## Web UI

Run option **2** from the menu or:
```bat
venv\Scripts\python.exe ui\app.py
```
Then open [http://127.0.0.1:5000](http://127.0.0.1:5000)

The dashboard shows:
- Live agent event feed
- Goal history and status
- Log viewer
- Model cache info
- Setup controls

Built with Flask + vanilla JS. Pure `#0B0B0B` void-black dark theme. No React, no Node, no build step.

---

## GitHub Integration

To have the Repo Manager auto-push completed goals to GitHub, add your token to `configs/config.json`:

```json
"github": {
  "enabled": true,
  "token": "ghp_your_token_here",
  "username": "your_github_username",
  "repo_name": "my-generated-code"
}
```

The system will create the repo if it doesn't exist, then push after each successful goal.

---

## Running Tests

```bat
venv\Scripts\python.exe -m pytest tests\ -v
```

Or use option **3** from `run.bat` to run the full self-validation suite, which checks file integrity, module imports, and runs the demo calculator tests end to end.

---

## How the memory works

Every agent action is logged to a local SQLite database (`memory/memory.db`):

```
events  → what every agent did, when, and why
goals   → status and iteration count per goal
tasks   → per-task assignment, result, and timestamps
```

This means you can inspect exactly what happened on any past run — no black boxes.

---

## Troubleshooting

**Window flashes and closes immediately**  
→ Use `run.bat`, not `main.py` directly. The bat file keeps the window open.

**`No module named 'flask'`**  
→ Dependencies aren't installed. Run `install_dependencies.bat` or just use `run.bat` which auto-installs on first launch.

**`torch` install fails**  
→ The installer tries the PyTorch CPU index automatically as a fallback. If it still fails, check your internet connection and retry.

**`sentencepiece` fails to build**  
→ This is a known issue on Python 3.14 — no prebuilt wheel exists yet. The installer skips it gracefully; the system works fine without it for TinyLlama.

**Model download is very slow**  
→ TinyLlama is ~2GB. It only downloads once and is cached in `models/cache/`. Subsequent runs are instant.

---

## License

MIT — do whatever you want with it.
