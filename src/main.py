import asyncio
import sys

# Third-party imports
from github.Issue import Issue
from semantic_kernel import Kernel

from comment_commands import CommentCommand, get_command_usage_markdown

# Local imports
from config import Config
from github_utils import (
    DISABLED_MARKER,
    GithubEvent,
    create_github_issue_comment,
    get_ai_enhanced_comment,
    get_github_comment,
    get_github_issue,
    is_agent_disabled,
    update_github_issue,
    get_existing_labels,
)
from openai_utils import initialize_kernel, run_completion
from prompts import build_user_story_eval_prompt
from response_models import UserStoryEvalResponse


async def handle_github_issues_event(
    issue: Issue, kernel: Kernel, existing_labels: list[str], is_manual_trigger: bool = False
) -> None:
    """
    Generate an AI-enhanced evaluation for a GitHub issue and post it as a comment if not disabled.

    Args:
        issue (Issue): The GitHub issue to process.
        kernel (Kernel): The initialized AI kernel for generating responses.
        existing_labels (list): List of existing labels in the repository.
        is_manual_trigger (bool): Whether this is a manual review request; defaults to False.
    """
    if not is_manual_trigger and is_agent_disabled(issue):
        print(f"Skipping automatic review for issue {issue.number} (disabled).")
        return
    messages = build_user_story_eval_prompt(issue.title, issue.body, existing_labels)

    try:
        response_text = await run_completion(kernel, messages)
        response_markdown = UserStoryEvalResponse.from_text(response_text).to_markdown()

        create_github_issue_comment(issue, response_markdown)
        print(f"AI Response for Issue {issue.number} (Markdown):\n\n{response_markdown}")
    except Exception as e:
        print(f"Error running Azure OpenAI completion: {e}", file=sys.stderr)
        sys.exit(1)


async def handle_github_comment_event(
    issue: Issue, issue_comment_id: int, kernel: Kernel, existing_labels: list[str]
) -> None:
    """
    Apply AI-suggested enhancements to a GitHub issue, or trigger a re-review if requested in a comment.

    Args:
        issue (Issue): The GitHub issue to update.
        issue_comment_id (int): The ID of the comment triggering the enhancement or review.
    """
    comment = get_github_comment(issue, issue_comment_id)
    comment_body = comment.body.strip().lower()

    if CommentCommand.APPLY.value in comment_body:
        ai_enhanced_comment = get_ai_enhanced_comment(issue)
        if ai_enhanced_comment is None:
            return

        user_story_eval = UserStoryEvalResponse.from_markdown(ai_enhanced_comment)

        update_github_issue(
            issue,
            title=user_story_eval.refactored.title,
            body=user_story_eval.refactored.body_markdown(),
            labels=user_story_eval.labels,
        )

        quoted_body = "\n".join([f"> {line}" for line in user_story_eval.to_markdown().strip().splitlines()])
        confirmation_comment = f"✅ Applied enhancements based on the following comment:\n\n" f"{quoted_body}"

        create_github_issue_comment(issue, confirmation_comment)

    elif CommentCommand.REVIEW.value in comment_body:
        print(f"Triggering manual review for issue {issue.number}...")

        await handle_github_issues_event(issue, kernel, existing_labels, is_manual_trigger=True)
    elif CommentCommand.USAGE.value in comment_body:
        usage_md = get_command_usage_markdown()
        create_github_issue_comment(issue, f"### 🤖 Available Commands\n\n{usage_md}")
        print(f"Posted usage information for issue {issue.number}.")
    elif CommentCommand.DISABLE.value in comment_body:
        create_github_issue_comment(
            issue,
            (
                f"🛑 Automatic reviews have been disabled for this issue. "
                f"Comment `{CommentCommand.REVIEW.value}` to manually trigger future evaluations."
                f"{DISABLED_MARKER}"
            ),
        )
    else:
        print(f"Comment {issue_comment_id} does not require processing.")


async def main() -> None:
    """
    Main entry point for the issue enhancer agent.

    Determines the GitHub event type and processes the issue or comment accordingly.
    """

    config = Config()

    github_issue = get_github_issue(
        token=config.github.token,
        repository=config.github.repository,
        issue_id=config.github.issue_id,
    )

    existing_labels = get_existing_labels(config.github.token, config.github.repository)

    print(f"Existing labels for repository '{config.github.repository}': {existing_labels}")
    print(f"Processing issue: {github_issue.title}")
    print(f"Event Name: {config.github.event_name}")

    kernel = initialize_kernel(
        azure_openai_target_uri=config.openai.azure_openai_target_uri,
        azure_openai_api_key=config.openai.azure_openai_api_key,
    )

    event_handlers = {
        GithubEvent.ISSUE: lambda: handle_github_issues_event(github_issue, kernel, existing_labels),
        GithubEvent.ISSUE_COMMENT: lambda: handle_github_comment_event(
            github_issue, config.github.issue_comment_id, kernel, existing_labels
        ),
    }

    handler = event_handlers.get(config.github.event_name)

    if handler:
        try:
            await handler()
        except Exception as e:
            print(f"Error during event handling: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Handler not defined for event: {config.github.event_name}")


if __name__ == "__main__":
    asyncio.run(main())
