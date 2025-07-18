# Python AI Workflow Agent

This repository contains a Python-based implementation of the AI Workflow Agent. The agent is designed to process GitHub issues using a structured workflow, including analyzing issue content, generating contextual comments, and posting them back to GitHub.

## Features

- **Issue Analysis**: Automatically determines the type, priority, and key topics of a GitHub issue.
- **Comment Generation**: Generates a detailed response comment based on the analysis.
- **GitHub Integration**: Posts comments and updates issue labels directly on GitHub.

## Requirements

- Python 3.9 or higher
- `PyGithub` library for GitHub API integration

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/sweanan/ai-workflow-agent.git
   cd ai-workflow-agent/python
   ```

2. Install dependencies:
   ```bash
   pip install -r src/requirements.txt
   ```

3. Build the Docker image:
   ```bash
   docker build -t python-ai-workflow-agent .
   ```

## Usage

### Running Locally

1. Set the required environment variables:
   - `INPUT_ISSUE_CONTENT`: Content of the GitHub issue
   - `INPUT_GITHUB_TOKEN`: GitHub personal access token
   - `INPUT_REPOSITORY`: Repository in the format `owner/repo`
   - `INPUT_ISSUE_NUMBER`: Issue number to process

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
              python-ai-workflow-agent
   ```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the terms of the LICENSE file.
