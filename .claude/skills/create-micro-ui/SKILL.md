---
name: create-micro-ui
description: Guide for creating a micro UI component. Use this when asked to create a new micro UI component or update an existing one. Micro UIs are used for communicating complex results to users.
---

# Guidelines
- Use resources at static/: Tailwind, FontAwesome, CAS Logo/Favicon, Highcharts, Luxon (for date management).
- Create singe HTML files to communicate ideas. 
- Use Vite for hot-reloading live changes to the UI.
- DO NOT HARD CODE NUMBERS, use variables and calculations instead. Each UI will have a source data object but everything else should be derived from that data.
- Source data should be at the top so it can easily be viewed/swapped. 
- Add the templates into the skill folder, but the agent will copy them to output/ so both locations will need to work (flexible imports please).
- Provide a command for swapping the data and copying the file into output/