# TPM Agent: AI-Powered GitHub Issue Enhancer

## Overview

TPM Agent is a GitHub Action that uses AI to analyze, evaluate, and improve GitHub issues, transforming them into high-quality user stories ready for engineering work. It leverages Azure OpenAI and Semantic Kernel to provide actionable feedback, suggest labels, and refactor stories for clarity, completeness, and testability.

## Features

- **AI-Driven Issue Evaluation:** Summarizes, checks completeness, and judges readiness of issues.
- **Refactored User Stories:** Suggests improved titles, descriptions, and acceptance criteria when needed.
- **Label Suggestions:** Recommends up to 3 relevant GitHub labels.
- **Markdown Round-Trip:** Robust parsing and formatting for seamless GitHub comment updates.
- **Input Validation:** Ensures all required inputs are present and valid.
- **Modular Codebase:** Clean separation of concerns for maintainability.

## Usage

### As a GitHub Action

This action is designed to run in a Docker container as part of your GitHub workflow. It requires configuration of environment variables for GitHub and Azure OpenAI access.

#### Example Workflow

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
    steps:
      - name: Run TPM Agent
        uses: mattdot/tpmagent@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          openai_api_key: ${{ secrets.AZURE_OPENAI_KEY }}
          openai_endpoint: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
          openai_deployment: ${{ secrets.AZURE_OPENAI_DEPLOYMENT }}
```

### Local Development

1. Clone the repo.

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run/test scripts in `src/` as needed.

## File Structure

- `src/main.py` - Entry point, event handling, AI integration
- `src/github_utils.py` - GitHub API helpers
- `src/openai_utils.py` - OpenAI/Semantic Kernel helpers
- `src/response_models.py` - Markdown parsing/generation
- `src/prompts.py` - Prompt construction
- `action.yml` - GitHub Action metadata
- `requirements.txt` - Python dependencies
- `.github/workflows/` - Example workflows

## Configuration

- Requires Azure OpenAI credentials and GitHub token as inputs or environment variables.
- See `action.yml` for all supported inputs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License. See [LICENSE](LICENSE).
