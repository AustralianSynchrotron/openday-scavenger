from datetime import datetime
from io import BytesIO

from segno import make_qr
from sqlalchemy.orm import Session

from openday_scavenger.api.puzzles.models import Puzzle, Response
from openday_scavenger.api.visitors.models import Visitor
from openday_scavenger.config import get_settings

from .exceptions import PuzzleCreationError, PuzzleNotFoundError, PuzzleUpdatedError
from .schemas import PuzzleCompare, PuzzleCreate, PuzzleUpdate

config = get_settings()


def get_all(db_session: Session, *, only_active: bool = False) -> list[Puzzle]:
    """Return all puzzles in the database, optionally only the active ones"""

    # Construct the database query dynamically, taking into account
    # whether only active puzzles should be returned.
    q = db_session.query(Puzzle)

    if only_active:
        q = q.filter(Puzzle.active)

    return q.all()


def get_all_responses(
    db_session: Session,
    *,
    filter_by_puzzle_name: str | None = None,
    filter_by_visitor_uid: str | None = None,
) -> list[Response]:
    """Return all puzzle responses in the database with optional filtering"""

    # Construct the database query dynamically. If the result needs to be filtered
    # by the first letters of the puzzle name or visitor uid, join the tables first
    # before applying the filter. We use ilike here, so the filter is case-insensitive.
    q = db_session.query(Response)

    if (filter_by_puzzle_name is not None) and (filter_by_puzzle_name != ""):
        q = q.join(Response.puzzle).filter(Puzzle.name.ilike(f"{filter_by_puzzle_name}%"))

    if (filter_by_visitor_uid is not None) and (filter_by_visitor_uid != ""):
        q = q.join(Response.visitor).filter(Visitor.uid.ilike(f"{filter_by_visitor_uid}%"))

    return q.all()


def create(db_session: Session, puzzle_in: PuzzleCreate) -> Puzzle:
    """Create a new puzzle entry in the database and return the entry"""

    # Create the database model object and pass in the pydantic schema values
    # explicitly. This maintains a nice abstraction between the service layer
    # and the database layer.
    puzzle = Puzzle(
        name=puzzle_in.name,
        answer=puzzle_in.answer,
        active=puzzle_in.active,
        location=puzzle_in.location,
        notes=puzzle_in.notes,
    )

    # Attempt adding the entry to the database. If it fails, roll back.
    try:
        db_session.add(puzzle)
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise PuzzleCreationError(f"Failed to create the puzzle {puzzle_in.name}")

    return puzzle


def update(db_session: Session, puzzle_name: str, puzzle_in: PuzzleUpdate) -> Puzzle:
    """Update a puzzle entry in the database and return the updated entry"""

    # Find the puzzle that should be updated in the database
    puzzle = db_session.query(Puzzle).filter(Puzzle.name == puzzle_name).first()
    if puzzle is None:
        raise PuzzleNotFoundError(
            f"A puzzle with the name {puzzle_name} could not be found in the database"
        )

    # We transform the input data which contains the fields with the new values
    # to a dictionary and in the process filter out any fields that have not been explicitly set.
    # This means any field in the pydantic model that has either not been touched or
    # has been assigned the default value is ignored.
    update_data = puzzle_in.model_dump(exclude_unset=True)

    # We map the pydantic model to the database model explicitly in order to maintain abstraction.
    puzzle.name = update_data.get("name", puzzle.name)
    puzzle.active = update_data.get("active", puzzle.active)
    puzzle.answer = update_data.get("answer", puzzle.answer)
    puzzle.location = update_data.get("location", puzzle.location)
    puzzle.notes = update_data.get("notes", puzzle.notes)

    # Attempt modifying the entry in the database. If it fails, roll back.
    try:
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise PuzzleUpdatedError(f"Failed to update the puzzle {puzzle_name}")

    return puzzle


def compare_answer(db_session: Session, puzzle_in: PuzzleCompare) -> bool:
    """Compare the provided answer with the stored answer and return whether it is correct"""

    # Get the database models for the puzzle so we can perform the answer comparison.
    puzzle = db_session.query(Puzzle).filter(Puzzle.name == puzzle_in.name).first()

    # We compare the provided answer with the stored answer. Currently this is a very simple
    # case sensitive string comparison. We can add more complicated comparison modes here later.
    is_correct = puzzle_in.answer == puzzle.answer

    # If the session management is turned off, skip the creation and storage
    # of a response as it is connected to a visitor uid.
    if config.SESSIONS_ENABLED:
        # Get the database model for the visitor so we can record who submitted the answer in the response table.
        visitor = db_session.query(Visitor).filter(Visitor.uid == puzzle_in.visitor).first()

        # Create a new response entry and store it in the database
        response = Response(
            visitor=visitor,
            puzzle=puzzle,
            answer=puzzle_in.answer,
            is_correct=is_correct,
            created_at=datetime.now(),
        )

        # Attempt adding the entry to the database. If it fails, roll back.
        try:
            db_session.add(response)
            db_session.commit()
        except:
            db_session.rollback()
            raise

    return is_correct


def generate_qr_code(name: str, as_file_buff: bool = False) -> str | BytesIO:
    _qr = make_qr(f"puzzles/{name}", error="H")

    if as_file_buff:
        buff = BytesIO()
        _qr.save(buff, kind="png")
        buff.seek(0)
        qr = buff
    else:
        qr = _qr.svg_data_uri()

    return qr


def generate_qr_codes_pdf(db_session: Session):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    puzzles = get_all(db_session, only_active=False)

    # Create a canvas object
    pdf_io = BytesIO()
    c = canvas.Canvas(pdf_io, pagesize=A4)
    width, height = A4

    # Calculate the position to center the QR code
    qr_size = 400  # Size of the QR code
    x = (width - qr_size) / 2
    y = (height - qr_size) / 2

    for puzzle in puzzles:
        # Draw the QR code image from BytesIO
        qr_code = generate_qr_code(puzzle.name, as_file_buff=True)
        qr_image = ImageReader(qr_code)
        c.drawImage(qr_image, x, y, width=qr_size, height=qr_size)

        # Set the font size for the URL text
        font_size = 24
        c.setFont("Helvetica", font_size)

        # Calculate the position to center the text
        text_width = c.stringWidth(f"/puzzle/{puzzle.name}", "Helvetica", font_size)
        text_x = (width - text_width) / 2

        # Add the URL text below the QR code
        c.drawString(text_x, y - 30, f"/puzzle/{puzzle.name}")

        # Create a new page for the next QR code
        c.showPage()

    c.save()
    pdf_io.seek(0)

    return pdf_io
