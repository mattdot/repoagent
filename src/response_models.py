import json
from typing import List, Optional


class UserStoryRefactored:
    """
    Model for the Refactored Story section in the AI response.
    """

    def __init__(
        self,
        title: str = "",
        description: str = "",
        acceptance_criteria: Optional[List[str]] = None,
    ):
        self.title = title
        self.description = description
        self.acceptance_criteria = acceptance_criteria

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            acceptance_criteria=data.get("acceptance_criteria", []),
        )

    @classmethod
    def from_markdown(cls, markdown: str):
        """
        Parse a markdown string and return a UserStoryRefactored instance.
        Handles both plain and bolded section headers.
        """
        title = ""
        description = ""
        acceptance_criteria = []
        lines = markdown.splitlines()
        section = None
        for line in lines:
            line_stripped = line.strip().lower()
            if line_stripped.startswith("**title**:"):
                title = line_stripped.split(":", 1)[-1].strip()
            elif line_stripped.startswith("**description**:"):
                description = line_stripped.split(":", 1)[-1].strip()
            elif line_stripped.startswith("**acceptance criteria**:"):
                section = "acceptance_criteria"
            elif section == "acceptance_criteria" and line_stripped.startswith("-"):
                acceptance_criteria.append(line_stripped.lstrip("- ").strip())
            elif section == "acceptance_criteria" and not line_stripped.startswith("-"):
                section = None
        return cls(
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
        )

    def to_markdown(self) -> str:
        """
        Convert the refactored story to a markdown string.
        """
        lines = []
        if self.title:
            lines.append(f"**Title**: {self.title}\n")
        body = self.body_markdown()
        if body:
            lines.append(body)
        return "\n".join(lines)

    def body_markdown(self) -> str:
        """
        Convert the description and acceptance criteria to a markdown string.
        """
        lines = []
        if self.description:
            lines.append(f"**Description**: {self.description}\n")
        if self.acceptance_criteria:
            lines.append("**Acceptance Criteria**:")
            for criterion in self.acceptance_criteria:
                lines.append(f"- {criterion}")
        return "\n".join(lines)


class UserStoryEvalResponse:
    """
    Model for parsing and representing the AI response from the user story evaluation prompt.
    """

    def __init__(
        self,
        summary: str,
        title_complete: bool,
        description_complete: bool,
        acceptance_criteria_complete: bool,
        importance: str,
        acceptance_criteria_evaluation: str,
        labels: List[str],
        ready_to_work: bool,
        base_story_not_clear: bool,
        refactored: Optional[UserStoryRefactored] = None,
    ):
        self.summary = summary
        self.title_complete = title_complete
        self.description_complete = description_complete
        self.acceptance_criteria_complete = acceptance_criteria_complete
        self.importance = importance
        self.acceptance_criteria_evaluation = acceptance_criteria_evaluation
        self.labels = labels
        self.ready_to_work = ready_to_work
        self.base_story_not_clear = base_story_not_clear
        self.refactored = refactored or UserStoryRefactored()

    @classmethod
    def from_text(cls, text: str):
        """
        Parse the AI response text (expected to be JSON) and return a UserStoryEvalResponse instance.
        """
        try:
            data = json.loads(text)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON from AI response: {e}\nRaw text: {text}")

        summary = data.get("summary", "")
        completeness = data.get("completeness", {})
        title_complete = completeness.get("title", "No").lower() == "yes"
        description_complete = completeness.get("description", "No").lower() == "yes"
        acceptance_criteria_complete = completeness.get("acceptance_criteria", "No").lower() == "yes"
        importance = data.get("importance", "")
        acceptance_criteria_evaluation = data.get("acceptance_criteria_evaluation", "")
        labels = data.get("labels", [])
        ready_to_work = bool(data.get("ready_to_work", False))
        base_story_not_clear = bool(data.get("base_story_not_clear", False))
        refactored = None
        if not ready_to_work and not base_story_not_clear and "refactored_story" in data:
            refactored = UserStoryRefactored.from_dict(data["refactored_story"])
        else:
            refactored = UserStoryRefactored()
        return cls(
            summary,
            title_complete,
            description_complete,
            acceptance_criteria_complete,
            importance,
            acceptance_criteria_evaluation,
            labels,
            ready_to_work,
            base_story_not_clear,
            refactored,
        )

    @classmethod
    def from_markdown(cls, markdown: str):
        """
        Parse a markdown string and return a UserStoryEvalResponse instance.
        """

        def emoji_to_bool(val: str) -> bool:
            return val.strip() == "✅"

        lines = markdown.splitlines()
        summary = ""
        title_complete = False
        description_complete = False
        acceptance_criteria_complete = False
        importance = ""
        acceptance_criteria_evaluation = ""
        labels = []
        ready_to_work = False
        base_story_not_clear = False
        refactored_md = []
        in_refactored = False
        for line in lines:
            if line.startswith("**Summary**:"):
                summary = line.split(":", 1)[-1].strip()
            elif line.strip().startswith("- Title:"):
                title_complete = emoji_to_bool(line.split(":", 1)[-1].strip())
            elif line.strip().startswith("- Description:"):
                description_complete = emoji_to_bool(line.split(":", 1)[-1].strip())
            elif line.strip().startswith("- Acceptance Criteria:"):
                acceptance_criteria_complete = emoji_to_bool(line.split(":", 1)[-1].strip())
            elif line.startswith("**Importance**:"):
                importance = line.split(":", 1)[-1].strip()
            elif line.startswith("**Acceptance Criteria Evaluation**:"):
                acceptance_criteria_evaluation = line.split(":", 1)[-1].strip()
            elif line.startswith("**Suggested Labels**:"):
                labels = [line_split.strip() for line_split in line.split(":", 1)[-1].split(",") if line_split.strip()]
            elif line.startswith("**Ready to Work**:"):
                ready_to_work = emoji_to_bool(line.split(":", 1)[-1].strip())
            elif "Base Story Not Clear:" in line:
                base_story_not_clear = emoji_to_bool(line.split(":", 1)[-1].strip())
            elif "could not be provided because the original story is unclear" in line:
                base_story_not_clear = True
            elif line.strip().startswith("### Refactored Story"):
                in_refactored = True
            elif in_refactored:
                refactored_md.append(line)
        refactored = UserStoryRefactored.from_markdown("\n".join(refactored_md)) if refactored_md else None
        return cls(
            summary,
            title_complete,
            description_complete,
            acceptance_criteria_complete,
            importance,
            acceptance_criteria_evaluation,
            labels,
            ready_to_work,
            base_story_not_clear,
            refactored,
        )

    def to_markdown(self) -> str:
        def yn_emoji(val: bool) -> str:
            return "✅" if val else "❌"

        lines = [
            "### 🤖 **AI-enhanced Evaluation**",
            f"**Summary**: {self.summary}",
            "**Completeness**:",
            f" - Title: {yn_emoji(self.title_complete)}\n",
            f" - Description: {yn_emoji(self.description_complete)}\n",
            f" - Acceptance Criteria: {yn_emoji(self.acceptance_criteria_complete)}\n\n",
            f"**Importance**: {self.importance}\n\n",
            f"**Acceptance Criteria Evaluation**: {self.acceptance_criteria_evaluation}\n\n",
            f"**Suggested Labels**: {', '.join(self.labels)}\n\n",
            f"**Ready to Work**: {yn_emoji(self.ready_to_work)}\n",
        ]
        if not self.ready_to_work and self.base_story_not_clear:
            lines.append(
                (
                    "\n**❌ Refactored Story could not be provided because the original story is unclear "
                    "or lacks meaningful value. Please rewrite the title and description to clearly explain "
                    "the story's purpose and value.**"
                )
            )
        if self.refactored and (not self.ready_to_work and not self.base_story_not_clear):
            lines.append("\n### Refactored Story")
            lines.append(self.refactored.to_markdown())
            lines.append("\n Reply `/apply` to apply these changes.\n")

        lines.append("\n Reply `/review` to run another evaluation.\n")
        lines.append("\n Reply `/usage` to see available commands.\n")

        return "\n".join(lines)
