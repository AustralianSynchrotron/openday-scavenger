# Australian Synchrotron Open Day Scavenger Hunt

The Open Day Scavenger Hunt is an interactive activity that the Scientific Computing team of the Australian Synchrotron is organising for the 2024 Open Day. This repository contains the complete web application for this activity.

Visitors of the Open Day will be tasked to solve little puzzles, scattered around the Australian Synchrotron facility. Each puzzle is connected to a QR code which, after scanning the code, is presented as a webpage to the visitor on their phone. By entering the correct answers, visitors solve the puzzles and can win prices.

During the Open Day a visitor is guided through the following steps:
1. The visitor registers at the registration desk by scanning a personalised QR code with their phone's camera or a QR scanner app. The code directs them to the scavenger hunt web application, generates an anonymous session and registers them in the application's database.
2. The visitor explores the facility and keeps an eye out for QR codes. If they find a QR code, they scan it with the scavenger hunt web application. The puzzle is displayed in the application.
3. The visitor solves the puzzle and enters their answer into the web application. The answer is compared with the correct answer stored in the database and they receive immediate feedback in the web application.
4. Once the visitor has solved all puzzles, they return to the registration desk and pick up their prize.


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


## The Visitor Flow
TBD

## Contribution
TBD


## Add a Puzzle
The heart and soul of the scavenger hunt web application are its puzzles. This sections describes the process of adding a puzzle and integrating it into the user experience and administration flow.

You will find a `demo` puzzle in the repository that you can use as an example or a basis for your own puzzle.


### Step 0: Preparation
The web application uses a simple Cookie-based session management to track visitors. This system is a little bit annoying when developing new puzzles. We recommend to turn it off during development by adding the following parameter to your `.env` file:
```
SESSIONS_ENABLED="false"
```


### Step 1: The Name
Pick a name for your puzzle. It should be one word (no whitespaces), can be a bit cryptic and needs to be unique among all puzzles. You will use the name in a few places, so coming up with a good initial name will make your life a lot easier.

We will use the very creative puzzle name of `demo` to illustrate the process in the following.

### Step 2: The Folder
Create a folder under `openday_scavenger/puzzles` with your puzzle name.

In our example you will find the `demo` puzzle under `openday_scavenger/puzzles/demo`

### Step 3: The Core Files
In your puzzle folder create a `__init__.py` file and a file that will host the routes for your puzzle, for instance `views.py`. You can create as many files in your folder as you like, but these two are the minimum you will need.

Within your routes file define the root route for your puzzle. You can define as many additional routes as you like, but we need at least one root route.

The following example doesn't implement a rendered puzzle page yet, but demonstrates the basics of a root route :
```Python
from fastapi import APIRouter

router = APIRouter()

@router.get('/')
async def index():
    return {"test": "test"}
```

### Step 4: Register your Puzzle Route
In order to make your puzzle visible to the world, register its API router. Attach it to the overarching puzzle router in the file `openday_scavenger/puzzles/__init__.py`.

Add an `import` and a `include_router` statement like the following to the list of puzzle routes:

```Python
from .[your puzzle name].views import router as puzzle_[your puzzle name]_router

router.include_router(puzzle_[your puzzle name]_router, prefix='/[your puzzle name]')
```

### Step 5: Enable your Puzzle
With your puzzle root route created and registered your puzzle will be available under `http://localhost:8000/puzzles/[your puzzle name]`

However, when you try to browse to your puzzle, you will be greeted with a "Unknown Puzzle" error. This is because we will need to add your puzzle to the database. While this seems like an unnecessary step first, having the puzzle added to the database allows us to not only store the correct answer to the puzzle in a central place but also enables us to take puzzles offline with the click of a button in case something is not working.

Browse to the puzzle administration area `http://localhost:8000/admin/puzzles` and add a your puzzle to the database by entering the name of your puzzle and click "Add new Puzzle".

Then click on the "Enable" button next to your puzzle. Now when you browse to `http://localhost:8000/puzzles/[your puzzle name]` you will see your puzzle.

### Step 6: Growing your Puzzle
The steps above are only the beginning of your puzzle implementation journey. You will most likely want to serve rendered web pages, possibly dynamic content via JavaScript and more.

The `demo` example in the repository uses a folder called `static` to host static assets such as the puzzle html page and jinja2 to render the page. Feel free to use this code as a starting point for your own puzzle.

### Step 7: Submitting a Puzzle Answer
At some point your puzzle will need to submit the visitor's answer and display whether it is correct or not. This is accomplished by sending a `POST` request to the endpoint `/submission` with the following content encoded as `multipart/form-data`:

| Key  | Value |
|----  | ------|
| visitor | The uid of the visitor submitting the answer |
| name | The name of your puzzle |
| answer | The answer that the visitor entered |

While the name of the puzzle and the answer is easy to collect, the visitor uid is a bit more complicated. You get the visitor uid from the authenticated visitor using the `get_auth_visitor` dependency:
```Python
from typing import Annotated
from fastapi import APIRouter, Request, Depends

from openday_scavenger.api.visitors.schemas import VisitorAuth
from openday_scavenger.api.visitors.dependencies import get_auth_visitor


router = APIRouter()

@router.get('/')
async def index(request: Request, visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)]):
    pass
```

After you made the request you will receive a response with the `JSON` body containing a boolean value indicating whether the asnwer was correct or not:
```JSON
{
    "success": True
}
```


## Architecture
TBD


## Technologies and Libraries
The scavenger hunt web application makes use of a mix of our standard libraries that we use in Scientific Computing and a few new ones that we wanted to try out.

| Library  | Reason |
| -------- | ------- |
| [uv](https://github.com/astral-sh/uv) | An extremely fast alternative to [Poetry](https://python-poetry.org). Poetry is our standard for dependency management and virtual environments, but this project provided a great opportunity to try out `uv`.
| [FastAPI](https://github.com/fastapi/fastapi)  | Our standard web framework for all RESTful and websocket APIs. |
| [SQLAlchemy](https://www.sqlalchemy.org)| Our standard ORM for SQL databases. |
| [jinja2](https://jinja.palletsprojects.com) | Our standard for templating, including the rendering of web pages. |
| [reportlab](https://docs.reportlab.com) | Our preferred library for generating PDF files. |
| [segno](https://github.com/heuer/segno)| A QR code generator that we like. |
| [ruff](https://github.com/astral-sh/ruff)| Our standard linter and code formatter for Python. |
| [mypy](https://mypy-lang.org)| Our standard type checker for Python. |
| [htmx](https://htmx.org) | We usually use [ReactJS](https://react.dev)/[NextJS](https://nextjs.org) for our web frontends. But those frameworks seemed too heavy for this project, thus we decided to give `htmx` a go for the common game and admin pages.  |
| [html5-qrcode](https://github.com/mebjas/html5-qrcode)| The QR scanner JavaScript library. This one seemed to work nicely and was least out of date of all the available QR scanner libraries. |
| [Bootstrap](https://getbootstrap.com) | We use a variety of styling libraries for our web services but for this project Bootstrap was the easiest and quickest way to introduce some decently styled components. |
