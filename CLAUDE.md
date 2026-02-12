Always follow these steps when working on this project:

If a file named PROGRESS.md does not already exist in the project directory:
- Copy .claude/skills/reserving-study/PROGRESS.md to a new file in the project directory.
- Use the AskUserQuestions tool to fill in the metadata at the top. 
- Make a commit.

Continue with the next step until all steps are complete.
- Use the AskUserQuestions tool at each step to get complete information.
- Update README.md with any new critical information or decisions along the way.

When a step is started: 
1. Mark it as "In Progress" 
2. Note the date. 

When a step is complete: mark it as "Complete", make a commit, note the date and commit ID and message.
1. Mark it as "Complete" 
2. Note any applicable scripts that were created
3. Make a commit
4. Note the date, commit ID and message.

As you go:
* Fill out project metadata in README.md as you learn more about the project. Try to intuit this from file names and content, etc. Only ask the user if you need to know right now.
* Mark any changes and decision in AUDIT.md. Include the date and user. Include commit ID if applicable.
* Track steps to replicate results in a file REPLICATE.md: files to add (w/ size and last modified date to verify correct file), scripts to run, any manual edits made to automatically generated files (with reasoning), etc.
* Create python scripts (use the python skill) at output/scripts/ as necessary to ensure the steps are repeatable. 
* Assume the user is not familiar with Git, they will rely on you to manage Git effectively on this project.
