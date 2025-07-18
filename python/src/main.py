import openai
import os
import logging
import re
import json
from github import Github

def classify_workitem(work_item):
    """
    Classify a work item as a bug or not using OpenAI's Chat Completion API.

    Args:
        work_item (dict): The work item to classify.

    Returns:
        str: Classification result (e.g., 'Bug' or 'Not a Bug').
    """
    # Read environment variables
    openai.api_type = os.getenv("INPUT_AZURE_OPENAI_API_TYPE", "azure")
    openai.api_key = os.getenv("INPUT_AZURE_OPENAI_KEY")
    openai.api_base = os.getenv("INPUT_AZURE_OPENAI_ENDPOINT")
    openai.api_version = os.getenv("INPUT_AZURE_OPENAI_API_VERSION")
    deployment_name = os.getenv("INPUT_AZURE_OPENAI_DEPLOYMENT")

    # Define system and user prompts
    #system_prompt = "You are a helpful software engineer assistant that classifies work items as bugs or not."
    system_prompt = """
        You are a helpful software engineer assistant that classifies work items as bugs or not.
        
        You will be provided with a work item number and description, and your task is to determine if it is a bug or story or feature by analyzing the content of the work item.
        If it is a bug, respond with "Bug". 
            If the work item is a bug, it should describe an issue or defect in the code that needs to be fixed.
            If the work item is a bug, it should include specific details about the problem, such as error messages, unexpected behavior, or steps to reproduce the issue.
        If it is story, respond with "Story".
        If it is a feature, respond with "Feature".
        If you are unsure, respond with "Uncertain" and provide a brief explanation.
        If the work item is a bug, review the work item description and related code to identify the root cause, include any potential resolution steps or suggestions for fixing the issue.
        If the work item is a bug, review the work item description and related code, and pose questions if unable to provide resolution steps.
        If the work item contains priority information, include it in your response.
        Provide your classification in the following format:
        ```json
        {
            "classification": "Bug"  # or "Story", "Feature", "Uncertain"
            "explanation": "Brief explanation of your classification decision."
            "priority": "Optional priority level for the work item, e.g., 'High', 'Medium', 'Low'.
            "resolution": "Optional resolution steps or suggestions if applicable. For example, 'Investigate the issue in the login module and fix the null pointer exception.'"
            "questions": "Optional questions for clarification if unable to provide resolution steps. For example, 'Could you provide more details about the error message encountered?'"
        }
        ```

        """
    
    
    user_prompt = f"Classify the following work item:\n{work_item}"

    # Call OpenAI's Chat Completion API
    response = openai.ChatCompletion.create(
        # model=config["model"],
        engine=deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    # Extract and return the classification result
    #print(response["choices"][0]["message"]["content"].strip())
    reply = response["choices"][0]["message"]["content"].strip()

    result = extract_json_from_response(response["choices"][0]["message"]["content"].strip())

    try:
        parsed_result = json.loads(result)
        classificationResult = parsed_result.get("classification", "Unknown")
    except json.JSONDecodeError:
        raise ValueError(f"❌ Model returned non-JSON: {result}")

    # return classificationResult
    return parsed_result, reply

def extract_json_from_response(reply):
    # Match first code block with json, fallback to raw content
    match = re.search(r"```json\s*(\{.*?\})\s*```", reply, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return reply.strip()

class IssueProcessingAgent:
    def __init__(self, logger, github_client):
        self.logger = logger
        self.github_client = github_client

    def process_issue(self, issue_content, repository, issue_number):
        self.logger.info(f"Processing issue {issue_number} in repository {repository}")

        # Classify the issue content
        parsed_result, reply = classify_workitem(issue_content)
        self.logger.info(f"Issue classification: {reply}")

        # Generate a comment based on the classification
        comment = self.generate_comment(parsed_result)
        self.logger.info(f"Generated comment: {comment}")

        # Post the comment to the issue
        # self.post_comment(repository, issue_number, json.dumps(parsed_result))
        self.post_comment(repository, issue_number, comment)

        # Add labels based on the analysis
        if 'classification' in parsed_result:
            self.logger.info(f"Adding label: {parsed_result['classification']}")
            self.add_labels(repository, issue_number, parsed_result['classification'])

        return parsed_result.get("classification", "Unknown")
        # return "Issue processed successfully"

    def generate_comment(self, parsed_result):
        comment = "Thank you for this issue!\n\n"
        comment += "## Analysis Results\n\n"
        comment += f"- **ClassificationType**: {parsed_result['classification']}\n"
        comment += f"- **Explanation**: {parsed_result['explanation']}\n"
        if 'priority' in parsed_result:
            comment += f"- **Priority**: {parsed_result['priority']}\n"
        comment += "\n## Next Steps\n\n"

        if parsed_result['classification'] == "bug":
            comment += "This appears to be a bug report. The development team will:\n"
            comment += "1. Review the issue details\n"
            comment += "2. Reproduce the issue if possible\n"
            comment += "3. Investigate the root cause\n"
            comment += "4. Provide a fix or workaround\n"
        elif parsed_result['classification'] == "feature":
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
    
    def add_labels(self, repository, issue_number, classification):
        owner, repo = repository.split('/')
        issue = self.github_client.get_repo(f"{owner}/{repo}").get_issue(number=issue_number)
        issue.add_to_labels(classification)
        self.logger.info("Added Labels successfully")

    def post_comment(self, repository, issue_number, comment):
        owner, repo = repository.split('/')
        self.logger.info(owner)
        self.logger.info(repo)
        self.logger.info(f"Posting comment to issue {issue_number} in repository {repository}")
        issue = self.github_client.get_repo(f"{owner}/{repo}").get_issue(number=issue_number)
        issue.create_comment(comment)
        # issue.add_to_labels("bug", "enhancement")
        self.logger.info("Comment posted successfully")

if __name__ == "__main__":
    # Load configuration
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