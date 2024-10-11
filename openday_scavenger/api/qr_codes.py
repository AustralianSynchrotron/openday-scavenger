import logging
from io import BytesIO
from pathlib import Path

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from segno import make_qr

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def generate_qr_code(
    url: str, as_file_buff: bool = False, logo: Path | None = None
) -> str | BytesIO:
    """Generates a QR code for the provided URL.

    Args:
        url (str): The URL to be encoded in the QR code.
        as_file_buff (bool, optional): If True, returns the QR code as a BytesIO object
            containing the PNG image data. Defaults to False, which returns the QR code as
            an SVG data URI string.
        logo (Path, optional): Pathlib Path to an image to use as a logo in middle of QR code. Must be
            compatible with `PIL.Image.open`. Logo is only created with `as_file_buff=True`.
            If the image is incompatible a warning is logged and QR code is created without the logo.
            Currently the ratio of logo to QR size is fixed at 1/25th.

    Returns:
        str | BytesIO: The QR code representation. If `as_file_buff` is True, a BytesIO
            object; otherwise, an SVG data URI string.
    """
    _qr = make_qr(f"{url}", error="H")
    qr_image = _qr.to_pil()  # type: ignore

    if logo is not None:
        qr_image = qr_image.convert("RGB")
        try:
            logo_image = Image.open(logo)
            qr_image = qr_image.resize((1000, 1000), Image.NEAREST)
            qr_width, qr_height = qr_image.size
            logo_width, logo_height = logo_image.size
            max_logo_size = min(qr_width // 5, qr_height // 5)
            ratio = min(max_logo_size / logo_width, max_logo_size / logo_height)
            logo_image = logo_image.resize(
                (int(logo_width * ratio), int(logo_height * ratio)), Image.BICUBIC
            )

            # Calculate the center position for the logo
            logo_x = (qr_width - logo_image.width) // 2
            logo_y = (qr_height - logo_image.height) // 2

            # Paste the logo onto the QR code image
            qr_image.paste(logo_image, (logo_x, logo_y))

        except Exception as e:
            logger.error(
                f"Opening and merging Logo {logo} with the qr code raised an exception {e}"
            )

    if as_file_buff:
        buff = BytesIO()
        qr_image.save(buff, format="png")
        buff.seek(0)
        qr = buff
    else:
        qr = _qr.svg_data_uri()

    return qr


def generate_qr_codes_pdf(
    entries: list[str],
    title: str = "blah",
    title_font_size: int = 14,
    url_font_size: int = 10,
    columns: int = 1,
    rows: int = 1,
    logo: Path | None = None,
) -> BytesIO:
    """Generates a PDF document containing QR codes for each URL in the provided list.

    Args:
        entries (list[str]): A list of URLs to be encoded as QR codes and included in
            the PDF.

    Returns:
        BytesIO: A BytesIO object containing the generated PDF document.
    """
    # Create a canvas object
    pdf_io = BytesIO()
    c = canvas.Canvas(pdf_io, pagesize=A4)
    width, height = A4

    x_margin = 50 / columns
    y_margin = 100

    qr_size = 500 / (rows)

    for i, entry in enumerate(entries):
        logger.info(f"Entry number {i}")
        col_index = i % columns
        row_index = 0 if i % (columns * rows) < 2 else 1

        x = x_margin + col_index * (qr_size + x_margin)
        y = height - (row_index + 1) * (qr_size + y_margin)

        # Set the font size for the Title text
        c.setFillColorRGB(0, 0.46, 0.75)
        c.setFont("Helvetica-Bold", title_font_size)

        # Calculate the position to center the text
        text_width = c.stringWidth(f"{title}", "Helvetica-Bold", title_font_size)
        text_x = x + (qr_size - text_width) / 2

        # Add the Title text above the QR code
        c.drawString(text_x, y + 510 / rows, f"{title}")

        # Draw the QR code image from BytesIO
        qr_code = generate_qr_code(entry, as_file_buff=True, logo=logo)
        qr_image = ImageReader(qr_code)
        c.drawImage(qr_image, x, y, width=qr_size, height=qr_size)

        # Set the font size for the URL text
        c.setFont("Helvetica", url_font_size)

        # Calculate the position to center the text
        text_width = c.stringWidth(f"{entry}", "Helvetica", url_font_size)
        text_x = x + (qr_size - text_width) / 2

        # Add the URL text below the QR code
        c.drawString(text_x, y, f"{entry}")

        # Create a new page for the next QR code
        if (i + 1) % (columns * rows) == 0:
            c.showPage()

    c.save()
    pdf_io.seek(0)

    return pdf_io
