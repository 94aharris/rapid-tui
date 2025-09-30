---
mode: agent
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/rapid-plan` in the triggering message **is** additional information to be considered during the following stage. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

With that in mind carry out the following tasks

1. Read the available research in the `.rapid/branch-name/research.md`
2. pass the available research to the rapid-planning-agent to create a comprehensive code implementation to that can be passed to the rapid-code-agent, and Store the code implementation plan in the `.rapid/branch-name/plan.md` file.
3. Confirm that the provided tasks have been completed with the user, and it is time to move on to the `/rapid-inspect` stage
