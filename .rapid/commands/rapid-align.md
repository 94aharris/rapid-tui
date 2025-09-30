---
description: Based on the researched information available and created by /research prompt. Starts an interactive session with the user to ask for any clarifying questions based on the research done for better planning alignment.
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/rapid-align` in the triggering message **is** additional information to be considered during the following stage. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

With that in mind carry out the following tasks

1. Read the available research in the `.rapid/branch-name/research.md`
2. If there are any CLARIFYING QUESTIONS, prompt the user and wait for their response
3. Update the `.rapid/branch-name/research.md` to remove answered questions and add clarified information
4. Confirm that the provided tasks have been completed with the user, and it is time to move on to the `/rapid-plan` stage.
