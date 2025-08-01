import sys
from enum import Enum
from typing import List, Tuple

from github import Github
from github.Issue import Issue

DISABLED_MARKER = "<!-- agent:disabled -->"


class GithubEvent(Enum):
    ISSUE = "issues"
    ISSUE_COMMENT = "issue_comment"


def is_agent_disabled(issue: Issue) -> bool:
    """
    Checks if the GitHub issue has a comment containing the disabled marker.

    Args:
        issue (Issue): The GitHub issue object.

    Returns:
        bool: True if the agent is disabled for this issue, False otherwise.
    """
    for comment in issue.get_comments():
        if DISABLED_MARKER in comment.body:
            return True
    return False


def has_label(issue: Issue, label_name: str) -> bool:
    """
    Check if a GitHub issue has a label with the given name (case-insensitive).

    Args:
        issue (Issue): The GitHub issue object.
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
        Issue: The fetched GitHub issue object.

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
        print(
            f"Error creating GitHub issue comment: {type(e).__name__}: {e}",
            file=sys.stderr,
        )
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


def get_repo_owner_and_name(repository: str) -> Tuple[str, str]:
    """
    Split a full GitHub repository string ('owner/repo') into owner and repo name.

    Args:
        repository (str): The repository string in 'owner/repo' format.

    Returns:
        Tuple[str, str]: A tuple containing (owner, repo_name)
    """
    try:
        owner, repo_name = repository.split("/", 1)
        return owner, repo_name
    except ValueError:
        raise ValueError(f"Invalid repository format: '{repository}'. Expected 'owner/repo'.")


def get_existing_labels(token: str, repository: str) -> List[str]:
    """
    Retrieve all label names defined in a given GitHub repository.

    Args:
        token (str): GitHub access token with permissions to read repository metadata.
        repository (str): The GitHub repository in 'owner/repo' format.

    Returns:
        List[str]: A list of label names (strings) currently defined in the repository.

    Raises:
        github.GithubException: If the repository cannot be accessed or labels cannot be fetched.
    """
    owner, repo = get_repo_owner_and_name(repository)
    github_client = Github(token)
    repo_obj = github_client.get_repo(f"{owner}/{repo}")
    return [label.name for label in repo_obj.get_labels()]
