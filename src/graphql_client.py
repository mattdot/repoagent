"""
GraphQL client for efficient GitHub issue fetching.

This module provides GraphQL-based issue fetching to reduce API calls and latency
compared to REST pagination. It includes retry logic, pagination support, and
early exit capabilities for disabled markers and AI comments.
"""

import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from github import Github, GithubException


@dataclass
class CommentNode:
    """Represents a single comment on a GitHub issue."""

    id: str
    db_id: Optional[int]
    body: str
    author: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class IssueSnapshot:
    """
    Snapshot of a GitHub issue with all relevant data fetched via GraphQL.

    This provides a complete view of an issue and its comments without requiring
    multiple API calls or dealing with pagination manually.
    """

    number: int
    title: str
    body: str
    state: str
    author: Optional[str]
    labels: list[str]
    comments: list[CommentNode]
    fetched_pages: int
    had_truncated: bool  # True if not all comments were fetched


class GraphQLExecutor:
    """
    Wrapper around PyGithub's GraphQL functionality.

    Provides retry logic and error handling for GraphQL queries.
    """

    def __init__(self, github_client: Github):
        """
        Initialize the GraphQL executor.

        Args:
            github_client: Authenticated PyGithub Github instance
        """
        self._github = github_client
        self._max_retries = 3
        self._base_backoff = 2  # seconds

    def execute(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a GraphQL query with retry logic.

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            Response data dictionary

        Raises:
            SystemExit: On authentication errors, permission errors, or after max retries
        """
        for attempt in range(self._max_retries):
            try:
                # PyGithub's graphql_query returns (headers, data)
                _, data = self._github.requester.graphql_query(query, variables)

                # Check for GraphQL errors
                if "errors" in data:
                    errors = data["errors"]
                    # Check for rate limit errors
                    for error in errors:
                        error_type = error.get("type", "")
                        if error_type in ["RATE_LIMITED", "INTERNAL"]:
                            if attempt < self._max_retries - 1:
                                backoff = self._base_backoff * (2**attempt)
                                print(f"GraphQL error (type: {error_type}), retrying in {backoff}s...", file=sys.stderr)
                                time.sleep(backoff)
                                continue
                            else:
                                print(f"GraphQL error after {self._max_retries} retries: {errors}", file=sys.stderr)
                                sys.exit(1)

                    # Other errors are fatal
                    print(f"GraphQL query error: {errors}", file=sys.stderr)
                    sys.exit(1)

                return data

            except GithubException as e:
                status = e.status

                # Authentication or permission errors are fatal
                if status in [401, 403]:
                    print(f"Authentication/permission error: {e}", file=sys.stderr)
                    sys.exit(1)

                # Retry on transient errors
                if status in [502, 503, 504] or status == -1:  # -1 is network error
                    if attempt < self._max_retries - 1:
                        backoff = self._base_backoff * (2**attempt)
                        print(f"Transient error (status {status}), retrying in {backoff}s...", file=sys.stderr)
                        time.sleep(backoff)
                        continue
                    else:
                        print(f"Error after {self._max_retries} retries: {e}", file=sys.stderr)
                        sys.exit(1)

                # Other errors are fatal
                print(f"GitHub API error: {e}", file=sys.stderr)
                sys.exit(1)

            except Exception as e:
                # Unexpected errors - retry once then fail
                if attempt < 1:
                    print(f"Unexpected error, retrying: {e}", file=sys.stderr)
                    time.sleep(self._base_backoff)
                    continue
                else:
                    print(f"Unexpected error after retry: {e}", file=sys.stderr)
                    sys.exit(1)

        # Should never reach here
        print("Max retries exceeded", file=sys.stderr)
        sys.exit(1)


def graphql_fetch_issue(
    executor: GraphQLExecutor,
    owner: str,
    repo: str,
    number: int,
    page_size: int = 100,
    after: Optional[str] = None,
) -> tuple[IssueSnapshot, dict[str, Any]]:
    """
    Fetch a GitHub issue with comments using GraphQL.

    Args:
        executor: GraphQL executor instance
        owner: Repository owner
        repo: Repository name
        number: Issue number
        page_size: Number of comments to fetch per page (max 100)
        after: Cursor for pagination (None for first page)

    Returns:
        Tuple of (IssueSnapshot, pageInfo dict with hasNextPage and endCursor)

    Raises:
        SystemExit: If issue not found or query fails
    """
    query = """
    query IssueWithComments($owner: String!, $name: String!, $number: Int!, $pageSize: Int!, $after: String) {
      repository(owner: $owner, name: $name) {
        issue(number: $number) {
          id
          number
          title
          body
          state
          url
          createdAt
          updatedAt
          author { login }
          labels(first: 50) { nodes { name color } }
          comments(first: $pageSize, after: $after) {
            totalCount
            pageInfo { hasNextPage endCursor }
            nodes {
              id
              databaseId
              body
              createdAt
              updatedAt
              author { login }
            }
          }
        }
      }
    }
    """

    variables = {
        "owner": owner,
        "name": repo,
        "number": number,
        "pageSize": page_size,
        "after": after,
    }

    data = executor.execute(query, variables)

    # Parse response
    repo_data = data.get("data", {}).get("repository")
    if not repo_data:
        print(f"Repository {owner}/{repo} not found", file=sys.stderr)
        sys.exit(1)

    issue_data = repo_data.get("issue")
    if not issue_data:
        print(f"Issue #{number} not found in {owner}/{repo}", file=sys.stderr)
        sys.exit(1)

    # Parse issue fields
    issue_number = issue_data["number"]
    title = issue_data.get("title", "")
    body = issue_data.get("body", "")
    state = issue_data.get("state", "OPEN")

    author_data = issue_data.get("author")
    author = author_data.get("login") if author_data else None

    # Parse labels
    labels_data = issue_data.get("labels", {}).get("nodes", [])
    labels = [label["name"] for label in labels_data if label]

    # Parse comments
    comments_data = issue_data.get("comments", {})
    comment_nodes = comments_data.get("nodes", [])
    page_info = comments_data.get("pageInfo", {})

    comments = []
    for node in comment_nodes:
        if not node:
            continue

        comment_author_data = node.get("author")
        comment_author = comment_author_data.get("login") if comment_author_data else None

        # Parse ISO 8601 timestamps
        created_at_str = node.get("createdAt", "")
        updated_at_str = node.get("updatedAt", "")

        try:
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            # Fallback to current time if parsing fails
            created_at = datetime.now()
            updated_at = datetime.now()

        comment = CommentNode(
            id=node.get("id", ""),
            db_id=node.get("databaseId"),
            body=node.get("body", ""),
            author=comment_author,
            created_at=created_at,
            updated_at=updated_at,
        )
        comments.append(comment)

    # Determine if this is the first page or a continuation
    fetched_pages = 1 if after is None else 0  # Will be incremented by caller
    had_truncated = page_info.get("hasNextPage", False)

    snapshot = IssueSnapshot(
        number=issue_number,
        title=title,
        body=body,
        state=state,
        author=author,
        labels=labels,
        comments=comments,
        fetched_pages=fetched_pages,
        had_truncated=had_truncated,
    )

    return snapshot, page_info


def paginate_issue_comments(
    executor: GraphQLExecutor,
    owner: str,
    repo: str,
    number: int,
    initial_snapshot: IssueSnapshot,
    disabled_marker: str,
    ai_comment_marker: str = "AI-enhanced Evaluation",
) -> IssueSnapshot:
    """
    Fetch additional comment pages if needed for disabled marker or AI comment detection.

    This function implements early exit: it stops fetching pages as soon as both
    the disabled marker and AI comment have been found (or determined to not exist).

    Args:
        executor: GraphQL executor instance
        owner: Repository owner
        repo: Repository name
        number: Issue number
        initial_snapshot: Initial snapshot from first page
        disabled_marker: HTML marker indicating agent is disabled
        ai_comment_marker: Marker for AI evaluation comments

    Returns:
        Updated IssueSnapshot with all relevant comments
    """
    snapshot = initial_snapshot

    if not snapshot.had_truncated:
        # All comments fetched in first page
        print(f"All comments fetched in initial page for issue #{number}")
        return snapshot

    # Track what we're looking for
    found_disabled = any(disabled_marker in comment.body for comment in snapshot.comments)
    found_ai_comment = any(ai_comment_marker.lower() in comment.body.lower() for comment in snapshot.comments)

    # If we found both, no need to continue
    if found_disabled and found_ai_comment:
        print(f"Found both markers in first page for issue #{number}")
        return snapshot

    # Fetch additional pages
    page_num = 2
    after_cursor = None

    # Get the page info from initial fetch
    _, page_info = graphql_fetch_issue(executor, owner, repo, number, page_size=100, after=None)
    after_cursor = page_info.get("endCursor")

    while after_cursor and (not found_disabled or not found_ai_comment):
        print(f"Fetching comment page {page_num} for issue #{number}")

        next_snapshot, page_info = graphql_fetch_issue(executor, owner, repo, number, page_size=100, after=after_cursor)

        # Append new comments
        snapshot.comments.extend(next_snapshot.comments)
        snapshot.fetched_pages = page_num
        snapshot.had_truncated = page_info.get("hasNextPage", False)

        # Check for markers in new comments
        if not found_disabled:
            found_disabled = any(disabled_marker in comment.body for comment in next_snapshot.comments)

        if not found_ai_comment:
            found_ai_comment = any(
                ai_comment_marker.lower() in comment.body.lower() for comment in next_snapshot.comments
            )

        # Early exit if both found
        if found_disabled and found_ai_comment:
            print(f"Found both markers after {page_num} pages for issue #{number}")
            break

        # Continue to next page if available
        if not page_info.get("hasNextPage", False):
            break

        after_cursor = page_info.get("endCursor")
        page_num += 1

    print(f"Fetched {snapshot.fetched_pages} page(s) for issue #{number}, " f"{len(snapshot.comments)} comments total")

    return snapshot
