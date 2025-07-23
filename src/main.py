import sys
import asyncio

# Third-party imports
from github.Issue import Issue
from semantic_kernel import Kernel

# Local imports
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
from utils import get_env_var
from response_models import UserStoryEvalResponse

COMMENT_LOOKUP = "/apply"

def handle_github_issues_event(issue: Issue, kernel: Kernel) -> None:
    """
    Handle GitHub issue events by generating and posting an AI-enhanced evaluation comment.
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
    Handle GitHub issue comment events by applying AI-suggested enhancements if requested.
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
    """Main entry point for the issue enhancer agent."""

    check_all = get_env_var(
        "INPUT_CHECK_ALL",
        required=False,
        cast_func=lambda v: str(v).strip().lower() in ["1", "true", "yes"],
        default=False,
    )
    github_event_name = get_env_var("INPUT_GITHUB_EVENT_NAME")
    github_issue_id = get_env_var("INPUT_GITHUB_ISSUE_ID", cast_func=int)
    github_token = get_env_var("INPUT_GITHUB_TOKEN")

    repository = get_env_var("GITHUB_REPOSITORY")

    if github_event_name not in [e.value for e in GithubEvent]:
        print(f"Error: Unsupported GitHub event: {github_event_name}", file=sys.stderr)
        sys.exit(1)

    github_issue = get_github_issue(
        token=github_token, repository=repository, issue_id=github_issue_id
    )

    if check_all and has_label(github_issue, GithubLabel.VTPM_IGNORE.value):
        print(
            f"Issue {github_issue_id} is ignored due to label {GithubLabel.VTPM_IGNORE.value}."
        )
        return

    if not check_all and not has_label(github_issue, GithubLabel.VTPM_REVIEW.value):
        print(
            f"Issue {github_issue_id} does not require review due to missing label {GithubLabel.VTPM_REVIEW.value}."
        )
        return

    print(f"Processing issue: {github_issue.title}")
    print(f"Event Name: {github_event_name}")

    if github_event_name == GithubEvent.ISSUE.value:

        azure_openai_target_uri = get_env_var("INPUT_AZURE_OPENAI_TARGET_URI")
        azure_openai_api_key = get_env_var("INPUT_AZURE_OPENAI_API_KEY")

        kernel = initialize_kernel(
            azure_openai_target_uri=azure_openai_target_uri,
            azure_openai_api_key=azure_openai_api_key,
        )

        handle_github_issues_event(github_issue, kernel)

    elif github_event_name == GithubEvent.ISSUE_COMMENT.value:

        github_issue_comment_id = get_env_var(
            "INPUT_GITHUB_ISSUE_COMMENT_ID"
        )
    
        handle_github_comment_event(github_issue, int(github_issue_comment_id))

    else:
        print(f"Unsupported GitHub event: {github_event_name}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
