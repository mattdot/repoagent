import os
import logging
from github import Github

class IssueProcessingAgent:
    def __init__(self, logger, github_client):
        self.logger = logger
        self.github_client = github_client

    def process_issue(self, issue_content, repository, issue_number):
        self.logger.info("Starting issue processing")

        # Analyze the issue
        analysis = self.analyze_issue(issue_content)

        # Generate a comment
        comment = self.generate_comment(analysis, issue_content)

        # Post the comment to GitHub
        self.post_comment(repository, issue_number, comment)
        
        # Add labels based on analysis
        self.add_labels(repository, issue_number, analysis)

        return "Issue processed successfully"

    def analyze_issue(self, issue_content):
        self.logger.info("Analyzing issue content")
        analysis = {}

        content = issue_content.lower()

        # Determine issue type
        if any(keyword in content for keyword in ["bug", "error", "issue"]):
            analysis['type'] = "bug"
        elif any(keyword in content for keyword in ["feature", "enhancement", "request"]):
            analysis['type'] = "feature"
        else:
            analysis['type'] = "question"

        # Determine priority
        if any(keyword in content for keyword in ["urgent", "critical", "high"]):
            analysis['priority'] = "high"
        elif "low" in content or "minor" in content:
            analysis['priority'] = "low"
        else:
            analysis['priority'] = "medium"

        # Extract key topics
        topics = []
        if "tpm" in content:
            topics.append("TPM")
        if "security" in content:
            topics.append("Security")
        if "docker" in content:
            topics.append("Docker")

        analysis['topics'] = topics
        return analysis

    def generate_comment(self, analysis, issue_content):
        comment = "Thank you for this issue!\n\n"
        comment += "## Analysis Results\n\n"
        comment += f"- **Type**: {analysis['type']}\n"
        comment += f"- **Priority**: {analysis['priority']}\n"
        if analysis['topics']:
            comment += f"- **Topics**: {', '.join(analysis['topics'])}\n"
        
        comment += "\n## Next Steps\n\n"

        if analysis['type'] == "bug":
            comment += "This appears to be a bug report. The development team will:\n"
            comment += "1. Review the issue details\n"
            comment += "2. Reproduce the issue if possible\n"
            comment += "3. Investigate the root cause\n"
            comment += "4. Provide a fix or workaround\n"
        elif analysis['type'] == "feature":
            comment += "This appears to be a feature request. The team will:\n"
            comment += "1. Evaluate the request against project goals\n"
            comment += "2. Assess implementation complexity\n"
            comment += "3. Consider adding it to the roadmap\n"
            comment += "4. Provide feedback on feasibility\n"
        else:
            comment += "This appears to be a question or general issue. The team will:\n"
            comment += "1. Review the details provided\n"
            comment += "2. Provide clarification or guidance\n"
            comment += "3. Update documentation if needed\n"

        return comment

    def post_comment(self, repository, issue_number, comment):
        owner, repo = repository.split('/')
        issue = self.github_client.get_repo(f"{owner}/{repo}").get_issue(number=issue_number)
        issue.create_comment(comment)
        # issue.add_to_labels("bug", "enhancement")
        self.logger.info("Comment posted successfully")

    def add_labels(self, repository, issue_number, analysis):
        owner, repo = repository.split('/')
        issue = self.github_client.get_repo(f"{owner}/{repo}").get_issue(number=issue_number)
        issue.add_to_labels(analysis['type'])
        self.logger.info("Added Labels successfully")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AI Workflow Agent")

    # Read environment variables
    issue_content = os.getenv("INPUT_ISSUE_CONTENT", "")
    github_token = os.getenv("INPUT_GITHUB_TOKEN", "")
    repository = os.getenv("INPUT_REPOSITORY", "")
    issue_number = os.getenv("INPUT_ISSUE_NUMBER", "")

    if not all([issue_content, github_token, repository, issue_number]):
        logger.error("Missing required environment variables")
        exit(1)

    try:
        github_client = Github(github_token)
        agent = IssueProcessingAgent(logger, github_client)
        result = agent.process_issue(issue_content, repository, int(issue_number))
        logger.info(result)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        exit(1)
