# MAIN OPERATION FLOW

Always follow these steps when working on this project:

If a file named PROGRESS.md does not already exist in the project directory: copy `.claude/PROGRESS.md` to a new file in the project directory.

Continue with the next step until all steps are complete.

When a step is started: 
1. Mark it as "In Progress" 
2. Note the date. 

When a step is complete: 
1. Mark it as "Complete" 
2. Note any applicable scripts that were created
3. Make a commit

As you go:
- Use the AskUserQuestions tool at each step to get complete information.
- Fill out project metadata in README.md as you learn more about the project. Try to intuit this from file names and content, etc. Only ask the user if you need to know right now.
- Mark any changes and decision in AUDIT.md. Include the date.
- Track steps to replicate results in a file REPLICATE.md: files to add (w/ size and last modified date to verify correct file), scripts to run, any manual edits made to automatically generated files (with reasoning), etc.
- Create python scripts (use the python skill) at output/scripts/ as necessary to ensure the steps are repeatable. 

# OTHER GUIDELINES

- Assume the user is not familiar with Git, they will rely on you to manage Git effectively on this project.
- Never include checkmarks or other unicode symbols in PowerShell commands - only use standard ASCII text and operators.
