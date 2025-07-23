from enum import Enum
from github import Github
from github.Issue import Issue
import sys

class GithubEvent(Enum):
    ISSUE = "issues"
    ISSUE_COMMENT = "issue_comment"

class GithubLabel(Enum):
    VSWE_ASSIGN = "vswe-assign"
    VTPM_REVIEW = "vtpm-review"
    VTPM_IGNORE = "vtpm-ignore"

def has_label(issue: Issue, label_name: str) -> bool:
    """
    Check if a GitHub issue has a label with the given name (case-insensitive).

    Args:
        issue (Issue.Issue): The GitHub issue object.
        label_name (str): The label name to check for.

    Returns:
        bool: True if the label exists, False otherwise.
    """
    if not hasattr(issue, "labels") or not isinstance(issue.labels, list):
        return False
    return any(getattr(label, "name", "").lower() == label_name.lower() for label in issue.labels)

def get_github_issue(token: str, repository: str, issue_id: int) -> Issue:
    """
    Fetch a GitHub issue by its ID.

    Args:
        token (str): GitHub access token.
        repository (str): Repository in 'owner/name' format.
        issue_id (int): The issue number.

    Returns:
        Issue.Issue: The fetched GitHub issue object.

    Raises:
        SystemExit: If the repository or issue cannot be found or accessed.
    """
    try:
        github_client = Github(token)
        repo = github_client.get_repo(repository)
        issue = repo.get_issue(issue_id)
        return issue
    except Exception as e:
        print(f"Error fetching GitHub issue: {e}", file=sys.stderr)
        sys.exit(1)


def create_github_issue_comment(issue: Issue, comment: str) -> bool:
    """
    Create a comment on a GitHub issue with detailed error reporting.

    Args:
        issue (Issue): The GitHub issue object.
        comment (str): The comment text to post.

    Returns:
        bool: True if the comment was created successfully, False otherwise.
    """
    try:
        issue.create_comment(comment)
        
        return True
    except Exception as e:
        print(f"Error creating GitHub issue comment: {type(e).__name__}: {e}", file=sys.stderr)
        return False

def get_ai_enhanced_comment(issue: Issue) -> str:
    """
    Get the AI-enhanced comment from the issue comments.

    Args:
        issue (Issue): The GitHub issue object.

    Returns:
        str: The content of the AI-enhanced comment, or None if not found.
    """
    for comment in reversed(list(issue.get_comments())):
        if "AI-enhanced Evaluation".lower() in comment.body.lower():
            print(f"Found AI-enhanced comment in issue #{issue.number} (comment id: {comment.id}).")
            return comment.body
    print(f"No AI-enhanced comment found in issue #{issue.number}.")
    return None

def get_github_comment(issue: Issue, comment_id: int):
    """
    Retrieve a specific comment by its ID from a GitHub issue.

    Args:
        issue (Issue): The GitHub issue object.
        comment_id (int): The ID of the comment to retrieve.

    Returns:
        The comment object if found.

    Raises:
        Exception: If the comment is not found or another error occurs.
    """
    try:
        comments = issue.get_comments()
        for comment in comments:
            if comment.id == comment_id:
                print(f"Found comment with id {comment_id} in issue #{issue.number}.")
                return comment
        raise Exception(f"Comment with id {comment_id} not found")
    except Exception as e:
        print(f"Error fetching GitHub comment: {type(e).__name__}: {e}", file=sys.stderr)
        raise

def update_github_issue(issue: Issue, title: str = None, body: str = None, labels: list = None) -> bool:
    """
    Update the title, body, or labels of a GitHub issue.

    Args:
        issue (Issue): The GitHub issue object.
        title (str, optional): New title for the issue.
        body (str, optional): New body for the issue.
        labels (list, optional): New labels for the issue.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        if title is not None and title != "":
            issue.edit(title=title)
            print(f"Updated title for issue #{issue.number}.")
        if body is not None and body != "":
            issue.edit(body=body)
            print(f"Updated body for issue #{issue.number}.")
        if labels is not None and labels != []:
            issue.edit(labels=labels)
            print(f"Updated labels for issue #{issue.number}.")
        return True
    except Exception as e:
        print(f"Error updating GitHub issue: {type(e).__name__}: {e}", file=sys.stderr)
        return False
