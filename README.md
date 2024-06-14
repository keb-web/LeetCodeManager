## Project
Discord bot that logs and send reminders of submitted LeetCode Questions & their progression history
Implemented in python with discord.py, aiosqlite, and (eventually) JS/REACT/DJANGO
**Main Purpose:** Practice and learn relational databases for upcoming database class in the Fall

## Dev Notes:
Small scale bot as it uses sqlite. Program can be expanded on for mass use with ... (MongoDB, mySQL??)

- TODO:
    - [x] implemnent relational tables with SQL lite
    - [-] implemnent async functionality with aiosqlite
    - [] Connect to Discord.py Commands
    - [] Scheduling / Notifications
    - [] implement basic frontend (Typescript practice)

- planned features
    - [-] History Logging
    - [] Reminders&interaction via Discord bot
    -[] Basic Front-end
        - gotta figure out how to link everything togetha first

- Misc.
    Show:
    - completed
    - Upcoming

    filter by:
    - Completed / Not Competed
    - Date Completed
    - Date Attempted
    - Number of Attempts
    - Question Type


FUTURE PLANS:
- [] Add tables (mySQL?) instead of using dictionaries. (good practice for fall class)
- [] Convert to typescript (good practice) and implement with tsamantanis/leetcode-api
- [] Fronted? (svelete?) [lowest-priority]

## Current Project Setup
will most def be changed in future..
-/ /assets      -> .svg pictures depictiing DB Table Relationships
-/ /LCM         -> python3 venv (Ignored in .gitignore)
-/ /.gitignore  -> ignoring shi
-/ /aioDB.py    -> Asyncronous implementation of (depreciated) 'database.py'
-/ /bot.py      -> Discord bot implemenation (Commands, I/O, Help Menu, Connections)
-/ /config.py   -> tokens (hidden in .gitignore)
-/ /database.py -> Old implementation of CLI LCM
-/ /README.md   -> this file
-/󰈙 /requirements.txt -> run `pip install -r requirements.txt` to install venv packages
-/ /schema.py   -> Const for 'aioDB' separated for readibility

___

### NEEDS TO BE UPDATED
Database Diagram (Idk if its accurate tbh...)
!["Database Diagram"](assets/LCMv2.svg)

---
## Obsidian notes:
WIP

---
## Project Reflection:
