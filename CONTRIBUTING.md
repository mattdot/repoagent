# Contributing Guide

Thank you for your interest in improving this project! This document outlines a lightweight workflow so you can get productive quickly.

## 🧱 Project Overview
- **Purpose:** AI-assisted evaluation and refinement of GitHub issues into actionable user stories.
- **Tech:** Python 3.11, Azure OpenAI (Semantic Kernel), Docker-based GitHub Action.

## 🔧 Environment Setup
```bash
pip install -r requirements.txt
```
Optional lint (if you add tooling):
```bash
pip install -r requirements-lint.txt
```

## ▶️ Running Locally
Issue evaluation (simulate `issues` event) using GitHub environment variables:
```bash
docker build -t repoagent .

# Create a GitHub event payload file
cat > /tmp/event.json << 'EOF'
{
  "issue": {
    "number": 123
  }
}
EOF

docker run --rm \
  -e GITHUB_EVENT_NAME=issues \
  -e GITHUB_EVENT_PATH=/tmp/event.json \
  -e GITHUB_TOKEN=ghp_xxx \
  -e GITHUB_REPOSITORY=owner/repo \
  -e INPUT_AZURE_OPENAI_API_KEY=xxx \
  -e INPUT_AZURE_OPENAI_TARGET_URI=https://<resource>.openai.azure.com/... \
  -v /tmp/event.json:/tmp/event.json:ro \
  repoagent
```

## ✅ Contribution Workflow
1. Fork & branch (`feat/<short-desc>` or `fix/<short-desc>`).
2. Make focused changes (keep PRs small & purposeful).
3. Add/update documentation when behavior changes.
4. Test parsing logic if you touch `response_models.py` (round‑trip markdown → model → markdown).
5. Open PR describing motivation, approach, and any limitations.

## 🧪 Evaluations
Use the optional evaluator harness:
```bash
cd evaluations
python evaluator.py
```
Configure Azure AI Foundry env vars per `evaluations/README.md`.

## 🧭 Code Style & Guidelines
- Favor clarity over cleverness.
- Keep public function/method signatures stable unless necessary.
- Keep prompts deterministic—avoid unstable phrasing changes.
- Log actionable errors; fail loudly on malformed AI JSON.

## 🔍 Areas Needing Help
| Area | Description |
| ---- | ----------- |
| Label filtering | `check_all` is reserved—feature unimplemented. |
| Tests | Add lightweight parsing & command flow tests. |
| Prompt tuning | Improve rejection handling for unclear stories. |
| Error resilience | Retry transient Azure OpenAI failures. |

## 🛡️ Security / Secrets
Never commit real API keys. Use placeholders in examples. Prefer repo secrets in workflows.

## 📜 License
By contributing you agree your contributions are licensed under the repository's MIT License.

## 🙌 Thanks
Your improvements help create cleaner, more actionable issues for everyone. Open a PR—even drafts are welcome!
