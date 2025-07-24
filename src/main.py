import sys
import asyncio

# Third-party imports
from github.Issue import Issue
from semantic_kernel import Kernel

# Local imports
from config import Config
from github_utils import (
    GithubEvent,
    GithubLabel,
    get_github_issue,
    get_github_comment,
    get_ai_enhanced_comment,
    has_label,
    create_github_issue_comment,
    update_github_issue,
)
from openai_utils import initialize_kernel, run_completion
from prompts import build_user_story_eval_prompt
from response_models import UserStoryEvalResponse

COMMENT_LOOKUP = "/apply"

def handle_github_issues_event(issue: Issue, kernel: Kernel) -> None:
    """
    Generate an AI-enhanced evaluation for a GitHub issue and post it as a comment.

    Args:
        issue (Issue): The GitHub issue to process.
        kernel (Kernel): The initialized AI kernel for generating responses.
    """
    messages = build_user_story_eval_prompt(issue.title, issue.body)

    try:
        response_text = asyncio.run(run_completion(kernel, messages))
        response = UserStoryEvalResponse.from_text(response_text).to_markdown()

        create_github_issue_comment(issue, response)
        print(f"AI Response for Issue {issue.number} (Markdown):\n\n{response}")
    except Exception as e:
        print(f"Error running Azure OpenAI completion: {e}", file=sys.stderr)
        sys.exit(1)


def handle_github_comment_event(issue: Issue, issue_comment_id: int) -> None:
    """
    Apply AI-suggested enhancements to a GitHub issue if requested in a comment.

    Args:
        issue (Issue): The GitHub issue to update.
        issue_comment_id (int): The ID of the comment triggering the enhancement.
    """
    comment = get_github_comment(issue, issue_comment_id)

    if COMMENT_LOOKUP not in comment.body:
        print(f"Comment {issue_comment_id} does not require processing.")
        return

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

    # Confirmation comment quoting the original enhancement comment
    confirmation_comment = (
        f"✅ Applied enhancements based on the following comment:\n\n"
        f"{quoted_body}"
    )

    create_github_issue_comment(
        issue, confirmation_comment
    )


def main() -> None:
    """
    Main entry point for the issue enhancer agent.

    Determines the GitHub event type and processes the issue or comment accordingly.
    """

    config = Config()

    github_issue = get_github_issue(
        token=config.github.token, repository=config.github.repository, issue_id=config.github.issue_id
    )

    if config.check_all and has_label(github_issue, GithubLabel.VTPM_IGNORE.value):
        print(
            f"Issue {config.github.issue_id} is ignored due to label {GithubLabel.VTPM_IGNORE.value}."
        )
        return

    if not config.check_all and not has_label(github_issue, GithubLabel.VTPM_REVIEW.value):
        print(
            f"Issue {config.github.issue_id} does not require review due to missing label {GithubLabel.VTPM_REVIEW.value}."
        )
        return

    print(f"Processing issue: {github_issue.title}")
    print(f"Event Name: {config.github.event_name}")

    event_handlers = {
        GithubEvent.ISSUE: lambda: handle_github_issues_event(
            github_issue,
            initialize_kernel(
                azure_openai_target_uri=config.openai.azure_openai_target_uri,
                azure_openai_api_key=config.openai.azure_openai_api_key,
            ),
        ),

        GithubEvent.ISSUE_COMMENT: lambda: handle_github_comment_event(
            github_issue, config.github.issue_comment_id
        ),
    }

    handler = event_handlers.get(config.github.event_name)
    if handler:
        handler()
    else:
        print(f"Unsupported event: {config.github.event_name}")



if __name__ == "__main__":
    main()
