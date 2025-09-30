---
mode: agent
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/rapid-research` in the triggering message **is** additional information to be used. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature or bug description, do this:

1. Read the information in `.rapid/branch-name/research-prompt.md` and use any additional information provided by the user.
2. Research the existing codebase for context that is relevant to the current feature or bug. Only gather context that is useful for development of the specific feature or remediation of the specified bug. This is information that is meant to be passed to a planning agent that will develop a comprehensive plan of how to carry out the implementation or the fix.
3. Output the collected research to a centralized context file under `.rapid/branch-name/research.md`. If there is any clarification needed then add then to the bottom of the file under CLARIFYING QUESTIONS.
4. Report completion with the research file path and the readiness for the next stage `/rapid-align`.
