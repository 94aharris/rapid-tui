---
description: Based on the plan.md file generated via the /rapid-plan command. Check and make sure that everything is correct and ready for implementation.
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/rapid-inspect` in the triggering message **is** additional information to be considered during the following stage. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

With that in mind carry out the following tasks

1. Read the plan in the `.rapid/branch-name/plan.md`
2. Display the plan to the user and verify that there is nothing that needs to be adjusted.
3. Update the `.rapid/branch-name/plan.md` with any recommended changes by the user if necessary.
4. Confirm that the provided tasks have been completed with the user, and it is time to move on to the `/rapid-develop` stage.
