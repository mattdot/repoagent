# Python TPM Agent

This repository contains a Python-based implementation of the TPM  Agent using OpenAI. The agent is designed to process GitHub issues using a structured workflow, including analyzing issue content using OpenAI, generating contextual comments, and posting them back to GitHub.

## Architecture

This action runs inside a Docker container and uses a python application built with OpenAI to analyze GitHub issues and provide intelligent responses. The container-based approach provides:

- **Isolation**: Each action run gets a fresh, isolated environment
- **Consistency**: Same runtime environment across different GitHub runners
- **OpenAI Integration**: Advanced AI-powered issue analysis and response generation
- **GitHub Integration**: Direct integration with GitHub API for issue commenting

## Components

- **Dockerfile**: Defines the container runtime environment with .NET 8.0 and required dependencies
- **C# Agent**: Semantic Kernel-based application that processes GitHub issues using Process Framework patterns
- **Entrypoint Script**: Orchestrates the container execution and GitHub Actions integration
- **GitHub API Integration**: Uses Octokit for GitHub API interactions

## Usage

### Basic Usage

```yaml
- name: Process GitHub Issue
  uses: mattdot/tpmagent/python@v1
  with:
    issue_content: ${{ github.event.issue.body }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
    repository: ${{ github.repository }}
    issue_number: ${{ github.event.issue.number }}
    azure_openai_api_type: ${{ secrets.AZURE_OPENAI_TYPE }}
    azure_openai_key: ${{ secrets.AZURE_OPENAI_KEY }}
    azure_openai_endpoint: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
    azure_openai_api_version: ${{ secrets.AZURE_OPENAI_API_VERSION }}
    azure_openai_deployment: ${{ secrets.AZURE_OPENAI_DEPLOYMENT }}
```

### Advanced Usage with Issue Events

```yaml
name: Process Issues
on:
  issues:
    types: [opened, edited]

jobs:
  process-issue:
    runs-on: ubuntu-latest
    steps:
      - name: Process Issue with TPM Agent
        uses: mattdot/tpmagent/python@v1
        with:
          issue_content: ${{ github.event.issue.body }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          repository: ${{ github.repository }}
          issue_number: ${{ github.event.issue.number }}
          azure_openai_api_type: ${{ secrets.AZURE_OPENAI_TYPE }}
          azure_openai_key: ${{ secrets.AZURE_OPENAI_KEY }}
          azure_openai_endpoint: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
          azure_openai_api_version: ${{ secrets.AZURE_OPENAI_API_VERSION }}
          azure_openai_deployment: ${{ secrets.AZURE_OPENAI_DEPLOYMENT }}
        id: issue-processor

      - name: Check Processing Results
        run: |
          echo "Processing Status: ${{ steps.issue-processor.outputs.status }}"
          echo "Processing Result: ${{ steps.issue-processor.outputs.result }}"
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `issue_content` | The content of the GitHub issue to process | Yes | - |
| `github_token` | GitHub token for API access | Yes | - |
| `repository` | Repository in the format owner/repo | Yes | - |
| `issue_number` | Issue number to comment on | Yes | - |
| `azure_openai_api_type` | Open AI API Type | Yes | - |
| `azure_openai_key` | Open AI API Key | Yes | - |
| `azure_openai_endpoint` | Open AI API Endpoint | Yes | - |
| `azure_openai_api_version` | Open AI API Version | Yes | - |
| `azure_openai_deployment` | Open AI API Deployment | Yes | - |

## Outputs

| Output | Description |
|--------|-------------|
| `result` | Result of the issue processing |
| `status` | Status of the operation (`success`, `error`) |


## Requirements

- Python 3.9 or higher
- `PyGithub` library for GitHub API integration

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/mattdot/repoagent.git
   cd repoagent/python
   ```

2. Install dependencies:
   ```bash
   pip install -r src/requirements.txt
   ```

3. Build the Docker image:
   ```bash
   docker build -t python-repoagent .
   ```

## Usage

### Running Locally

1. Set the required environment variables:
   - `INPUT_ISSUE_CONTENT`: Content of the GitHub issue
   - `INPUT_GITHUB_TOKEN`: GitHub personal access token
   - `INPUT_REPOSITORY`: Repository in the format `owner/repo`
   - `INPUT_ISSUE_NUMBER`: Issue number to process
   - `INPUT_AZURE_OPENAI_ENDPOINT`: Azure OpenAI Endpoint
   - `INPUT_AZURE_OPENAI_DEPLOYMENT`: Azure OpenAI Deployment
   - `INPUT_AZURE_OPENAI_API_VERSION`: Azure OpenAI Version
   - `INPUT_AZURE_OPENAI_KEY`: Azure OpenAI Key
   - `INPUT_AZURE_OPENAI_TYPE`: Azure OpenAI Type

2. Run the script:
   ```bash
   python src/main.py
   ```

### Running with Docker

1. Run the Docker container:
   ```bash
   docker run -e INPUT_ISSUE_CONTENT="<issue_content>" \
              -e INPUT_GITHUB_TOKEN="<github_token>" \
              -e INPUT_REPOSITORY="<owner/repo>" \
              -e INPUT_ISSUE_NUMBER="<issue_number>" \
              -e INPUT_AZURE_OPENAI_ENDPOINT="<Azure OpenAI Endpoint>" \
              -e `INPUT_AZURE_OPENAI_DEPLOYMENT="<Azure OpenAI Deployment>" \
              -e INPUT_AZURE_OPENAI_API_VERSION="<Azure OpenAI Version>" \
              -e INPUT_AZURE_OPENAI_KEY="<Azure OpenAI Key>" \
              -e INPUT_AZURE_OPENAI_TYPE="<Azure OpenAI Type>" \
              python-repoagent
   ```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the terms of the LICENSE file.
