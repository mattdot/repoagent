# AI-Powered GitHub Issue Enhancer

## Overview

An AI-powered GitHub Action that analyzes, evaluates, and (optionally) refactors GitHub issues into high-quality user stories. It uses Azure OpenAI (via Semantic Kernel) to provide structured feedback, suggest existing repository labels, and generate an improved story only when appropriate.

## Key Features & Benefits

| Feature | What It Does | Why It Matters |
|---------|--------------|----------------|
| Structured AI Evaluation | Produces a concise summary plus completeness flags (title, description, acceptance criteria), importance, and readiness status. | Quickly surfaces gaps so authors know exactly what to improve—reduces reviewer back‑and‑forth. |
| Context-Aware Refactored Story | Generates an improved title, description, and acceptance criteria only when the original is clear but incomplete. | Avoids noisy rewrites; delivers value-added refinement without overwriting already good work. |
| Existing Label Suggestions | Suggests up to 3 labels strictly from the repository's current label set. | Ensures consistency with existing taxonomy; prevents accidental creation of near-duplicate labels. |
| Deterministic Markdown Round‑Trip | Parses its own prior comments and regenerates output safely. | Allows iterative `/review` cycles without formatting drift or duplicated sections. |
| Command Workflow (`/review`, `/apply`, `/usage`, `/disable`) | Users drive when to re-evaluate, apply changes, view help, or pause automation. | Transparent, reversible control keeps humans in charge of changes to issues. |
| Safe Disable Mechanism | Embeds a hidden HTML marker to stop future automatic evaluations. | Lightweight opt-out per issue with an easy path to re-enable by removing the marker. |
| Evaluation Harness (`evaluations/`) | Optional script to score agent output (task adherence, intent resolution, completeness). | Enables data-driven tuning and regression checks for prompt / logic changes. |
| Minimal Required Inputs | Leverages `GITHUB_REPOSITORY` env and only requires comment ID for comment events. | Reduces configuration errors and speeds adoption. |
| Immutable Config Layer | Centralized, read-only configuration objects (`config.py`). | Lowers risk of side-effects and simplifies reasoning about runtime behavior. |
| Clear Refactor Conditions | Skips refactored story if issue is already “ready” or unclear. | Prevents misleading auto-generated content and focuses effort where it yields ROI. |

> TL;DR: The agent elevates raw issue text into implementable user stories with targeted, non-intrusive assistance—accelerating grooming while preserving maintainers' control.

## Workflow Usage

The action runs inside a Docker container. Azure OpenAI credentials are required for both `issues` and `issue_comment` events.

### Example Workflow

```yaml
name: AI Issue Enhancer
on:
  issues:
    types: [opened, edited]
  issue_comment:
    types: [created]

jobs:
  enhance:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - name: Run Repo Agent
        uses: mattdot/repoagent@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          github_event_name: ${{ github.event_name }}
          github_issue_id: ${{ github.event.issue.number }}
          # github_issue_comment_id: ${{ github.event.comment.id }} # Only for issue_comment events
          azure_openai_api_key: ${{ secrets.AZURE_OPENAI_API_KEY }}
          azure_openai_target_uri: ${{ secrets.AZURE_OPENAI_TARGET_URI }}
          check_all: false
```

## Local Development

```bash
pip install -r requirements.txt
```

Run individual modules (e.g. parsing) as needed from `src/`.

## Local Testing with Docker

Issue event simulation:

```bash
docker build -t repoagent .
docker run --rm \
  -e INPUT_GITHUB_EVENT_NAME=issues \
  -e INPUT_GITHUB_ISSUE_ID=123 \
  -e INPUT_GITHUB_TOKEN=ghp_xxx \
  -e INPUT_AZURE_OPENAI_API_KEY=xxx \
  -e INPUT_AZURE_OPENAI_TARGET_URI=https://<resource>.openai.azure.com/openai/deployments/<deployment>/chat/completions?api-version=2024-XX-XX \
  -e GITHUB_REPOSITORY=owner/repo \
  repoagent
```

Issue comment event simulation (adds comment id):

```bash
docker run --rm \
  -e INPUT_GITHUB_EVENT_NAME=issue_comment \
  -e INPUT_GITHUB_ISSUE_ID=123 \
  -e INPUT_GITHUB_ISSUE_COMMENT_ID=456 \
  -e INPUT_GITHUB_TOKEN=ghp_xxx \
  -e INPUT_AZURE_OPENAI_API_KEY=xxx \
  -e INPUT_AZURE_OPENAI_TARGET_URI=https://<resource>.openai.azure.com/... \
  -e GITHUB_REPOSITORY=owner/repo \
  repoagent
```

`GITHUB_REPOSITORY` is read from the environment (no explicit action input required at runtime).

## File Structure

- `src/main.py` – Entry point, event flow
- `src/github_utils.py` – GitHub API helpers & disable marker logic
- `src/openai_utils.py` – Azure OpenAI / Semantic Kernel orchestration
- `src/response_models.py` – JSON ↔ markdown parsing & serialization
- `src/prompts.py` – Prompt construction
- `evaluations/` – Offline evaluation harness (Azure AI evaluators)
- `action.yml` – Action metadata / inputs
- `requirements.txt` – Runtime dependencies

## Inputs

All action inputs map to environment variables `INPUT_<NAME>` automatically. Azure OpenAI credentials are needed for both supported events.

| Input Name | Required | Events | Description |
| ---------- | -------- | ------ | ----------- |
| `github_event_name` | Yes | all | Event name (`issues` or `issue_comment`) |
| `github_issue_id` | Yes | all | Issue number to process |
| `github_issue_comment_id` | No (Yes for `issue_comment`) | issue_comment | Comment id that triggered the run |
| `github_token` | Yes | all | Token with `issues:write` permission |
| `azure_openai_api_key` | Yes | all | Azure OpenAI API key |
| `azure_openai_target_uri` | Yes | all | Full chat completions endpoint URL |
| `check_all` | No | issues | (Reserved) future bulk processing flag |
| `repository` | No | all | (Unused) repository is taken from `GITHUB_REPOSITORY` env |

Notes:
1. `repository` is currently not read by the code; the runtime uses the standard `GITHUB_REPOSITORY` environment variable.
2. `github_issue_comment_id` is only needed when the triggering event is `issue_comment`.

### Refactored Story Conditions

A `refactored_story` section is included only when:

- `ready_to_work` is false AND
- `base_story_not_clear` is false

If the story is already good (`ready_to_work = true`) or unclear (`base_story_not_clear = true`), no refactored story is generated (an explanatory note is shown for the unclear case).

## Supported Workflow Events

- `issues` – Evaluate newly opened / edited issues.
- `issue_comment` – Execute commands (`/apply`, `/review`, etc.).

## Commands

| Command | Purpose | Notes |
| ------- | ------- | ----- |
| `/review` | Run (or re-run) an evaluation and post results. | Use iteratively as issue evolves. |
| `/apply` | Apply latest AI-refactored title/body/labels. | Only works if a prior evaluation comment exists. |
| `/usage` | Show help / command list. | Always available. |
| `/disable` | Stop automatic AI evaluations for this issue. | Adds a hidden HTML marker. Remove the marker & comment `/review` to re-enable. |

Disable marker used: `<!-- agent:disabled -->`.

## Evaluations Harness

The `evaluations/` folder provides `evaluator.py` leveraging Azure AI Foundry evaluators (Task Adherence, Intent Resolution, Response Completeness). See `evaluations/README.md` for environment variable requirements and execution steps:

```bash
cd evaluations
python evaluator.py
```

## Security / Permissions

Grant the workflow only the permissions it needs (minimum: `issues: write`, `contents: read`). Secrets required: Azure OpenAI key and target URI.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT – see [LICENSE](LICENSE).
