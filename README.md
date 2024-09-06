# Australian Synchrotron Open Day Scavenger Hunt

The Open Day Scavenger Hunt is an interactive activity that the Scientific Computing team of the Australian Synchrotron is organising for the 2024 Open Day. This repository contains the complete web application for this activity.

Visitors of the Open Day will be tasked to solve little puzzles, scattered around the Australian Synchrotron facility. Each puzzle is connected to a QR code which, after scanning the code, is presented as a webpage to the visitor on their phone. By entering the correct answers, visitors solve the puzzles and can win prices.

During the Open Day a visitor is guided through the following steps:
1. The visitor registers at the registration desk by scanning a personalised QR code with their phone's camera or a QR scanner app. The code directs them to the scavenger hunt web application, generates an anonymous session and registers them in the application's database.
2. The visitor explores the facility and keeps an eye out for QR codes. If they find a QR code, they scan it with the scavenger hunt web application. The puzzle is displayed in the application.
3. The visitor solves the puzzle and enters their answer into the web application. The answer is compared with the correct answer stored in the database and they receive immediate feedback in the web application.
4. Once the visitor has solved all puzzles, they return to the registration desk and pick up their price.


## Installation
The web application is written in Python, the language of choice for the Scientific Computing team at the Australian Synchrotron. The following sections explain two methods to install and run the application locally.

### Option 1: Use Virtual Environments
This is the quickest and easiest method to run the scavenger hunt web application. It uses a local database and demonstrates the power of virtual environments for local Python development.

#### Setup
The web application makes use of [`uv`](https://github.com/astral-sh/uv) for installing dependencies and creating the virtual environment.

If you don't have `uv` installed yet, get it on Linux with:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
For other operating systems please see [here](https://docs.astral.sh/uv/getting-started/installation).


The application requires Python 3.12. If you don't have this version installed yet, the easiest way is to use `uv`:
```
uv python install 3.12
```

Install all the dependencies inside a virtual environment with:
```
uv sync
```

#### Run the Application
Run the web application using its internal development server with:
```
uv run fastapi dev ./openday_scavenger/main.py
```

If you want to modify the code, start the server with auto-reloading to avoid having to manually restart the application after code changes:
```
uv run fastapi dev ./openday_scavenger/main.py --reload
```

Open a web browser and go to `http://localhost:8000`.

#### Persistent Data
By default, the web application will use an in-memory sqlite database. If you like to persist the data over restarts of the application, use a file based sqlite database. Create a `.env` file in the repository's root folder with the following content (you can adjust the filename to your liking):
```
DATABASE_SCHEME=sqlite
DATABASE_NAME="scavenger_hunt.db"
```
Restart the server and it will pick up the settings automatically.

### Option 2: use devcontainers
TBD


## Contribution
TBD


## Add a Puzzle
TBD


## Architecture
TBD


## Technologies
TBD
