from enum import Enum

class CommentCommand(Enum):
    APPLY =  "/apply"
    REVIEW = "/review"
    USAGE =  "/usage"
    DISABLE = "/disable"

COMMAND_DESCRIPTIONS = {
    CommentCommand.APPLY: "Applies the AI-enhanced title, body, and labels to the issue.",
    CommentCommand.REVIEW: "Re-runs the AI review and posts a fresh evaluation as a comment.",
    CommentCommand.USAGE: "Displays this list of available commands.",
    CommentCommand.DISABLE: "Disables the repo agent for this issue, preventing further auto reviews.",
}

def get_command_usage_markdown() -> str:
    lines = [
        "| Command | Description |",
        "|---------|-------------|",
    ]
    for command, description in COMMAND_DESCRIPTIONS.items():
        lines.append(f"| `{command.value}` | {description} |")
    return "\n".join(lines)
