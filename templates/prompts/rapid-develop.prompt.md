---
mode: agent
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/rapid-develop` in the triggering message **is** additional information to be considered during the following stage. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

With that in mind carry out the following tasks

1. Read the available research in the `.rapid/branch-name/plan.md`
2. Pass the plan to the rapid-coding-agent to complete the code implementation.
3. Confirm that the provided tasks have been completed with the user.
