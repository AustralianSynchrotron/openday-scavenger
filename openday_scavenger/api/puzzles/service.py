from io import BytesIO
from datetime import datetime
from segno import make_qr
from sqlalchemy.orm import Session

from openday_scavenger.api.puzzles.models import Puzzle, Response
from openday_scavenger.api.visitors.models import Visitor

from .schemas import PuzzleCompare, PuzzleCreate, PuzzleUpdate


def get_all(db_session: Session, *, only_active: bool = False) -> list[Puzzle]:
    q = db_session.query(Puzzle)
    if only_active:
        q = q.filter(Puzzle.active)
    return q.all()


def create(db_session: Session, puzzle_in: PuzzleCreate):
    puzzle = Puzzle(
        name=puzzle_in.name,
        answer=puzzle_in.answer,
        active=puzzle_in.active,
        location=puzzle_in.location,
        notes=puzzle_in.notes,
    )

    db_session.add(puzzle)

    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise

    return puzzle


def update(db_session: Session, puzzle_name: str, puzzle_in: PuzzleUpdate):
    puzzle = db_session.query(Puzzle).filter(Puzzle.name == puzzle_name).first()

    update_data = puzzle_in.model_dump(exclude_unset=True)

    # map the pydantic model to database model explicitly to maintain abstraction
    puzzle.name = update_data.get("name", puzzle.name)
    puzzle.active = update_data.get("active", puzzle.active)
    puzzle.answer = update_data.get("answer", puzzle.answer)
    puzzle.location = update_data.get("location", puzzle.location)
    puzzle.notes = update_data.get("notes", puzzle.notes)

    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise

    return puzzle


def compare_answer(db_session: Session, puzzle_in: PuzzleCompare) -> bool:
    """ Compare the provided answer with the stored answer and return whether it is correct """

    # Get the database models for the puzzle so we can perform the answer comparison.
    # Also get the database model for the visitor so we can record who submitted the answer in the reponse table.
    puzzle = db_session.query(Puzzle).filter(Puzzle.name == puzzle_in.name).first()
    visitor = db_session.query(Visitor).filter(Visitor.uid == puzzle_in.visitor_uid).first()

    # We compare the provided answer with the stored answer. Currently this is a very simple
    # case sensitive string comparison. We can add more complicated comparison modes here later.
    is_correct = (puzzle_in.answer == puzzle.answer)

    # Create a new response entry and store it in the database
    response = Response(
        visitor=visitor,
        puzzle=puzzle,
        answer=puzzle_in.answer,
        is_correct=is_correct,
        created_at=datetime.now()
    )

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
