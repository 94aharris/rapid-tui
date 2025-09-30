---
description: Creates a new git workspace and creates helps the user to create a descriptive rapid research prompt to be passed to /rapid-research.
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/rapid-init` in the triggering message **is** the feature or bug description. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature or bug description, do this:

1. If a Task Number is provided then run the get feature script like `python .rapid/scripts/get_feature.py <Task_Number>`
2. Create a new git worktree in `../` based on the feature description and or task. Make sure that the branch and worktree name are succinct and include the task number if one.
3. Switch to the new git worktree that was created.
4. Use the information provided by the user and the Feature description and acceptance criteria if any to formulate a verbose feature prompt that
   can be passed to a research agent like the prompts in the EXAMPLE below.
5. Validate that the prompt is correct with the user
6. once the prompt is validated by the user then store it in `.rapid/branch-name/research-prompt.md`

EXAMPLE PROMPT: Search Export Additions - As a User I want the search results export to now include both URL and date. The search result export datapicker dialog should now contain these options preselected by default. If one or the other is selected then it should appear in the table preview and in the downloaded excel file once exported.
