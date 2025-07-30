from enum import Enum


class CommentCommand(Enum):
    APPLY = "/apply"
    REVIEW = "/review"
    USAGE = "/usage"


COMMAND_DESCRIPTIONS = {
    CommentCommand.APPLY: "Applies the AI-enhanced title, body, and labels to the issue.",
    CommentCommand.REVIEW: "Re-runs the AI review and posts a fresh evaluation as a comment.",
    CommentCommand.USAGE: "Displays this list of available commands.",
}


def get_command_usage_markdown() -> str:
    lines = [
        "| Command | Description |",
        "|---------|-------------|",
    ]
    for command, description in COMMAND_DESCRIPTIONS.items():
        lines.append(f"| `{command.value}` | {description} |")
    return "\n".join(lines)
