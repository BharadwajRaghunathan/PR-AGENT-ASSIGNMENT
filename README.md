# PR Review Agent

A Python-based backend agent for reviewing pull requests on GitHub (extensible to GitLab/Bitbucket). Analyzes code for structure, standards, and bugs, with scoring and AI-driven suggestions.

## Tech Stack
- Python: Core language.
- Git: API integration via PyGithub.
- AI: Simulated suggestions (use CodeMate Extension for real AI).
- Code Review: pylint and flake8.
- Software Engineering: Modular design, PEP 8.
- Backend: CLI with optional Flask web interface.

## Setup
1. Clone: `git clone https://github.com/BharadwajRaghunathan/PR-AGENT-ASSIGNMENT.git`
2. Install: `pip install -r requirements.txt`
3. Add .env with GITHUB_TOKEN (fine-grained PAT with read access to contents/pull requests).
4. Run CLI: `python main.py --repo owner/repo --pr 1`
5. Run Web: `python main.py --web` (access http://127.0.0.1:5000/)

## Features
- Fetches PRs from GitHub (multi-server extensible).
- Analyzes code with pylint/flake8.
- Generates feedback with score and AI suggestions.

For hackathon: Use CodeMate Build/Extension for AI and debugging.