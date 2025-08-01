# flake8: noqa: E501

SYSTEM_PROMPT = "You are a helpful assistant that analyzes and improves GitHub issues using natural language. All responses must be valid JSON."


def build_user_story_eval_prompt(issue_title: str, issue_body: str) -> list:
    prompt = (
        f"## GitHub Issue Context\n"
        f"Title: {issue_title}\n"
        f"Body: {issue_body}\n\n"
        "## Evaluation Instructions\n"
        "You must return your response as a single valid JSON object. Do not include any markdown, code blocks, or extra commentary.\n\n"
        "Assess the issue as a candidate user story for engineering work. Your response must include the following fields:\n"
        "- summary: A concise, AI-enhanced summary or insight about the story.\n"
        "- completeness: An object with keys 'title', 'description', and 'acceptance_criteria', each with values 'Yes' or 'No'.\n"
        "- importance: Why the story matters (business value, user need, technical dependency).\n"
        "- acceptance_criteria_evaluation: Analysis of the acceptance criteria for clarity, specificity, and testability via automation. If not automatable, include a warning and suggest improvements.\n"
        "- labels: An array of up to 3 relevant GitHub labels (e.g. 'bug', 'enhancement', 'good first issue').\n"
        "- ready_to_work: Boolean. True if all elements are present, clear purpose, and testable acceptance criteria.\n"
        "- base_story_not_clear: Boolean. True if the title or description is vague, placeholder-like, or lacks meaningful value (e.g. 'Test', 'TBD', 'No update provided').\n"
        "- refactored_story: An object with keys 'title', 'description', and 'acceptance_criteria' (an array of strings). Only include this if ready_to_work is False AND base_story_not_clear is False. If any field is unchanged, copy it verbatim from the original.\n\n"
        "If base_story_not_clear is True or ready_to_work is True, omit the 'refactored_story' field entirely.\n\n"
        "Example JSON response:\n"
        "{\n"
        '  "summary": "<your insight>",\n'
        '  "completeness": {\n'
        '    "title": "Yes",\n'
        '    "description": "Yes",\n'
        '    "acceptance_criteria": "No"\n'
        "  },\n"
        '  "importance": "<why it matters>",\n'
        '  "acceptance_criteria_evaluation": "<analysis + any testability warning>",\n'
        '  "labels": ["bug", "enhancement"],\n'
        '  "ready_to_work": false,\n'
        '  "base_story_not_clear": false,\n'
        '  "refactored_story": {\n'
        '    "title": "Refined or original title",\n'
        '    "description": "Expanded or original explanation with business value or user need",\n'
        '    "acceptance_criteria": [\n'
        '      "criterion one",\n'
        '      "criterion two"\n'
        "    ]\n"
        "  }\n"
        "}\n"
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
