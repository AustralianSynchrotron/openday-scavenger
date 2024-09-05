# Australian Synchrotron Open Day Scavenger Hunt

The Australian Synchrotron Open Day Scavenger Hunt is an interactive activity that the Scientific Computing group is organising for the 2024 Open Day. This repository contains the web application for this activity.

Visitors of the Open Day will be tasked to solve little puzzles, scattered around the Australian Synchrotron facility. Each puzzle is connected to a QR code that, after scanning the code, is presented as a webpage on their phone. By entering the correct answer to the puzzle, visitors solve the puzzle and can win prices.

The steps a visitor follows during the Open Day are as follows:
1. The visitor registers at the registration desk by scanning a personalised QR code with their phone's camera or a QR scanner app. The code directs them to the scavenger hunt web application, generates an anonymous session and registers them in the application's database.
2. The visitor explores the facility and keeps an eye out for QR codes. If they find a QR code they scan it with the scavenger hunt web application. The puzzle is displayed in the application.
3. The visitor solves the puzzle and enters their answer into the scavenger hunt web application. Their answer is compared with the correct answer.
4. Once they have solved all puzzles the visitors return to the registration desk and pick up their price.


## Installation

### Option 1: use virtual environments

The scavenger hunt web application makes use of `uv` for installing dependencies and creating the virtual environment.

If you don't have `uv` installed yet, get it on Linux with:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

The application requires Python 3.12. If you don't have this version yet, the easiest way is to use `uv` to install it:
```
uv python install 3.12
```

Install all the packages and create the virtual environment with:
```
uv sync
```

Run the web application using its development server and auto-reloading with:
```
uv run fastapi dev ./openday_scavenger/main.py --reload
```

By default, it will use an in-memory sqlite database. If you like to persist the data over restarts of the web application, you can use a file based sqlite database.
Create a `.env` file in the repository's root folder with the following content (you can adjust the filename to your liking):
```
DATABASE_SCHEME=sqlite
DATABASE_NAME="scavenger_hunt.db"
```


### Option 2: use devcontainers
TBD

## Contribution
TBD

### Add a Puzzle
TBD

