"""
Centralized configuration and environment variable handling for repoagent.
"""

from github_utils import GithubEvent
from utils import get_env_var

from typing import Any, Optional


class GitHubConfig:
    """
    Handles GitHub-related configuration values and validation.
    Parses and validates environment variables for GitHub events, issue IDs, tokens, repository, and comment IDs.
    Raises ValueError if required variables are missing or invalid.
    """

    def __init__(self):
        event_name_str: str = get_env_var("INPUT_GITHUB_EVENT_NAME")

        try:
            self.event_name: GithubEvent = GithubEvent(event_name_str)
        except ValueError:
            raise ValueError(
                f"Invalid event name: {event_name_str}. Must be one of {[e.value for e in GithubEvent]}"
            )

        self.issue_id: int = get_env_var(
            "INPUT_GITHUB_ISSUE_ID", cast_func=int
        )
        self.token: str = get_env_var("INPUT_GITHUB_TOKEN")
        self.repository: str = get_env_var("GITHUB_REPOSITORY")

        if self.event_name == GithubEvent.ISSUE_COMMENT:
            self.issue_comment_id: int = get_env_var(
                "INPUT_GITHUB_ISSUE_COMMENT_ID", cast_func=int
            )
        else:
            self.issue_comment_id: Optional[int] = get_env_var(
                "INPUT_GITHUB_ISSUE_COMMENT_ID", cast_func=int, required=False
            )


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
        self.check_all: bool = get_env_var(
            "INPUT_CHECK_ALL", default=False, cast_func=self._cast_bool, required=False
        )
        self.github = GitHubConfig()
        self.openai = OpenAIConfig()
        self._initialized = True

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Prevents modification of config values after initialization.
        """
        if hasattr(self, "_initialized") and self._initialized and name != "_initialized":
            raise AttributeError(
                f"Config is immutable. Cannot modify '{name}' after initialization."
            )
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