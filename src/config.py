"""
Centralized configuration and environment variable handling for repoagent.
"""

from typing import Any, Optional

from github_utils import GithubEvent
from utils import get_env_var, get_github_event_payload


class GitHubConfig:
    """
    Handles GitHub-related configuration values and validation.
    Parses and validates environment variables for GitHub events, issue IDs, tokens, repository, and comment IDs.
    Raises ValueError if required variables are missing or invalid.
    """

    def __init__(self):
        # Get event name from INPUT_GITHUB_EVENT_NAME or fallback to GITHUB_EVENT_NAME
        event_name_str: str = get_env_var("INPUT_GITHUB_EVENT_NAME", required=False)
        if not event_name_str:
            event_name_str = get_env_var("GITHUB_EVENT_NAME", required=True)

        try:
            self.event_name: GithubEvent = GithubEvent(event_name_str)
        except ValueError:
            raise ValueError(f"Invalid event name: {event_name_str}. Must be one of {[e.value for e in GithubEvent]}")

        # Get event payload for extracting issue and comment IDs
        event_payload = get_github_event_payload()

        # Get issue ID from INPUT or event payload
        issue_id_str = get_env_var("INPUT_GITHUB_ISSUE_ID", required=False)
        if issue_id_str:
            self.issue_id: int = int(issue_id_str)
        elif event_payload and "issue" in event_payload and "number" in event_payload["issue"]:
            self.issue_id: int = event_payload["issue"]["number"]
        else:
            raise ValueError(
                "Missing required issue ID: set INPUT_GITHUB_ISSUE_ID or "
                "ensure GITHUB_EVENT_PATH contains issue.number"
            )

        # Get token from INPUT_GITHUB_TOKEN or fallback to GITHUB_TOKEN
        self.token: str = get_env_var("INPUT_GITHUB_TOKEN", required=False)
        if not self.token:
            self.token = get_env_var("GITHUB_TOKEN", required=True)

        # Repository is already correctly read from GITHUB_REPOSITORY
        self.repository: str = get_env_var("GITHUB_REPOSITORY")

        # Get comment ID from INPUT or event payload
        if self.event_name == GithubEvent.ISSUE_COMMENT:
            comment_id_str = get_env_var("INPUT_GITHUB_ISSUE_COMMENT_ID", required=False)
            if comment_id_str:
                self.issue_comment_id: int = int(comment_id_str)
            elif event_payload and "comment" in event_payload and "id" in event_payload["comment"]:
                self.issue_comment_id: int = event_payload["comment"]["id"]
            else:
                raise ValueError(
                    "Missing required comment ID for issue_comment event: set INPUT_GITHUB_ISSUE_COMMENT_ID or "
                    "ensure GITHUB_EVENT_PATH contains comment.id"
                )
        else:
            comment_id_str = get_env_var("INPUT_GITHUB_ISSUE_COMMENT_ID", required=False)
            if comment_id_str:
                self.issue_comment_id: Optional[int] = int(comment_id_str)
            else:
                self.issue_comment_id: Optional[int] = None


class OpenAIConfig:
    """
    Handles OpenAI/Azure-related configuration values.
    Parses environment variables for Azure OpenAI target URI and API key.
    """

    def __init__(self):
        self.azure_openai_target_uri: str = get_env_var("INPUT_AZURE_OPENAI_TARGET_URI")
        self.azure_openai_api_key: str = get_env_var("INPUT_AZURE_OPENAI_API_KEY")


class Config:
    """
    Centralized config class for environment variable and input handling.
    Groups GitHub and OpenAI config, and enforces immutability after initialization.
    Use this class to access all configuration values for the repoagent project.
    """

    check_all: bool
    github: GitHubConfig
    openai: OpenAIConfig

    def __init__(self) -> None:
        self._initialized: bool = False
        self.check_all: bool = get_env_var("INPUT_CHECK_ALL", default=False, cast_func=self._cast_bool, required=False)
        self.github = GitHubConfig()
        self.openai = OpenAIConfig()
        self._initialized = True

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Prevents modification of config values after initialization.
        """
        if hasattr(self, "_initialized") and self._initialized and name != "_initialized":
            raise AttributeError(f"Config is immutable. Cannot modify '{name}' after initialization.")
        super().__setattr__(name, value)

    def _cast_bool(self, val: str) -> bool:
        """
        Casts a string value to boolean using common truthy values.
        """
        return str(val).strip().lower() in ["1", "true", "yes"]

    def get(self, key: str, default: Any = None) -> Any:
        """
        Returns the value of a config attribute, or a default if not present.
        """
        return getattr(self, key, default)
