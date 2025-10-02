import sys
from enum import Enum
from typing import List, Union

from github import Github
from github.Issue import Issue

from graphql_client import (
    GraphQLExecutor,
    IssueSnapshot,
    graphql_fetch_issue,
    paginate_issue_comments,
)

DISABLED_MARKER = "<!-- agent:disabled -->"


class GithubEvent(Enum):
    ISSUE = "issues"
    ISSUE_COMMENT = "issue_comment"


def is_agent_disabled(issue: Union[Issue, IssueSnapshot]) -> bool:
    """
    Checks if the GitHub issue has a comment containing the disabled marker.

    Args:
        issue (Issue | IssueSnapshot): The GitHub issue object or snapshot.

    Returns:
        bool: True if the agent is disabled for this issue, False otherwise.
    """
    if isinstance(issue, IssueSnapshot):
        # Check comments in snapshot
        for comment in issue.comments:
            if DISABLED_MARKER in comment.body:
                return True
        return False
    else:
        # Original PyGithub Issue object
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


def get_github_issue(token: str, repository: str, issue_id: int) -> IssueSnapshot:
    """
    Fetch a GitHub issue by its ID using GraphQL for efficiency.

    Args:
        token (str): GitHub access token.
        repository (str): Repository in 'owner/name' format.
        issue_id (int): The issue number.

    Returns:
        IssueSnapshot: The fetched GitHub issue snapshot with comments.

    Raises:
        SystemExit: If the repository or issue cannot be found or accessed.
    """
    try:
        github_client = Github(token)
        owner, repo = repository.split("/", 1)

        # Create GraphQL executor
        executor = GraphQLExecutor(github_client)

        # Fetch initial page
        print(f"Fetching issue #{issue_id} from {repository} via GraphQL...")
        snapshot, _ = graphql_fetch_issue(executor, owner, repo, issue_id, page_size=100)

        # Fetch additional pages if needed for marker detection
        if snapshot.had_truncated:
            snapshot = paginate_issue_comments(executor, owner, repo, issue_id, snapshot, DISABLED_MARKER)

        print(f"Fetched issue #{issue_id}: {len(snapshot.comments)} comments, " f"{snapshot.fetched_pages} page(s)")

        return snapshot
    except Exception as e:
        print(f"Error fetching GitHub issue: {e}", file=sys.stderr)
        sys.exit(1)


def get_pygithub_issue(token: str, repository: str, issue_id: int) -> Issue:
    """
    Fetch a PyGithub Issue object for operations that require it (comments, updates).

    This is a helper for backward compatibility with functions that need the
    PyGithub Issue object for mutations.

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
        print(f"Error fetching PyGithub issue: {e}", file=sys.stderr)
        sys.exit(1)


def create_github_issue_comment(
    issue: Union[Issue, IssueSnapshot], comment: str, token: str = None, repository: str = None
) -> bool:
    """
    Create a comment on a GitHub issue with detailed error reporting.

    Args:
        issue (Issue | IssueSnapshot): The GitHub issue object or snapshot.
        comment (str): The comment text to post.
        token (str, optional): GitHub token (required if issue is IssueSnapshot).
        repository (str, optional): Repository in 'owner/name' format (required if issue is IssueSnapshot).

    Returns:
        bool: True if the comment was created successfully, False otherwise.
    """
    try:
        if isinstance(issue, IssueSnapshot):
            # Need to fetch PyGithub Issue to create comment
            if not token or not repository:
                raise ValueError("token and repository are required when using IssueSnapshot")
            pygithub_issue = get_pygithub_issue(token, repository, issue.number)
            pygithub_issue.create_comment(comment)
        else:
            # Original PyGithub Issue object
            issue.create_comment(comment)
        return True
    except Exception as e:
        print(
            f"Error creating GitHub issue comment: {type(e).__name__}: {e}",
            file=sys.stderr,
        )
        return False


def get_ai_enhanced_comment(issue: Union[Issue, IssueSnapshot]) -> str:
    """
    Get the AI-enhanced comment from the issue comments.

    Args:
        issue (Issue | IssueSnapshot): The GitHub issue object or snapshot.

    Returns:
        str: The content of the AI-enhanced comment, or None if not found.
    """
    if isinstance(issue, IssueSnapshot):
        # Check comments in snapshot (reversed to get most recent first)
        for comment in reversed(issue.comments):
            if "AI-enhanced Evaluation".lower() in comment.body.lower():
                print(f"Found AI-enhanced comment in issue #{issue.number} (comment id: {comment.id}).")
                return comment.body
        print(f"No AI-enhanced comment found in issue #{issue.number}.")
        return None
    else:
        # Original PyGithub Issue object
        for comment in reversed(list(issue.get_comments())):
            if "AI-enhanced Evaluation".lower() in comment.body.lower():
                print(f"Found AI-enhanced comment in issue #{issue.number} (comment id: {comment.id}).")
                return comment.body
        print(f"No AI-enhanced comment found in issue #{issue.number}.")
        return None


def get_github_comment(issue: Union[Issue, IssueSnapshot], comment_id: int):
    """
    Retrieve a specific comment by its ID from a GitHub issue.

    Args:
        issue (Issue | IssueSnapshot): The GitHub issue object or snapshot.
        comment_id (int): The ID of the comment to retrieve.

    Returns:
        The comment object if found (CommentNode for IssueSnapshot, PyGithub comment for Issue).

    Raises:
        Exception: If the comment is not found or another error occurs.
    """
    try:
        if isinstance(issue, IssueSnapshot):
            # Search in snapshot comments
            for comment in issue.comments:
                if comment.db_id == comment_id:
                    print(f"Found comment with id {comment_id} in issue #{issue.number}.")
                    return comment
            raise Exception(f"Comment with id {comment_id} not found")
        else:
            # Original PyGithub Issue object
            comments = issue.get_comments()
            for comment in comments:
                if comment.id == comment_id:
                    print(f"Found comment with id {comment_id} in issue #{issue.number}.")
                    return comment
            raise Exception(f"Comment with id {comment_id} not found")
    except Exception as e:
        print(f"Error fetching GitHub comment: {type(e).__name__}: {e}", file=sys.stderr)
        raise


def update_github_issue(
    issue: Union[Issue, IssueSnapshot],
    title: str = None,
    body: str = None,
    labels: list = None,
    token: str = None,
    repository: str = None,
) -> bool:
    """
    Update the title, body, or labels of a GitHub issue.

    Args:
        issue (Issue | IssueSnapshot): The GitHub issue object or snapshot.
        title (str, optional): New title for the issue.
        body (str, optional): New body for the issue.
        labels (list, optional): New labels for the issue.
        token (str, optional): GitHub token (required if issue is IssueSnapshot).
        repository (str, optional): Repository in 'owner/name' format (required if issue is IssueSnapshot).

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        if isinstance(issue, IssueSnapshot):
            # Need to fetch PyGithub Issue to update
            if not token or not repository:
                raise ValueError("token and repository are required when using IssueSnapshot")
            pygithub_issue = get_pygithub_issue(token, repository, issue.number)
            issue_number = issue.number
        else:
            # Original PyGithub Issue object
            pygithub_issue = issue
            issue_number = issue.number

        if title is not None and title != "":
            pygithub_issue.edit(title=title)
            print(f"Updated title for issue #{issue_number}.")
        if body is not None and body != "":
            pygithub_issue.edit(body=body)
            print(f"Updated body for issue #{issue_number}.")
        if labels is not None and labels != []:
            pygithub_issue.edit(labels=labels)
            print(f"Updated labels for issue #{issue_number}.")
        return True
    except Exception as e:
        print(f"Error updating GitHub issue: {type(e).__name__}: {e}", file=sys.stderr)
        return False


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
    github_client = Github(token)
    repo_obj = github_client.get_repo(repository)
    return [label.name for label in repo_obj.get_labels()]
