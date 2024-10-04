from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from segno import make_qr


def generate_qr_code(url: str, as_file_buff: bool = False) -> str | BytesIO:
    """Generates a QR code for the provided URL.

    Args:
        url (str): The URL to be encoded in the QR code.
        as_file_buff (bool, optional): If True, returns the QR code as a BytesIO object
            containing the PNG image data. Defaults to False, which returns the QR code as
            an SVG data URI string.

    Returns:
        str | BytesIO: The QR code representation. If `as_file_buff` is True, a BytesIO
            object; otherwise, an SVG data URI string.
    """
    _qr = make_qr(f"{url}", error="H")

    if as_file_buff:
        buff = BytesIO()
        _qr.save(buff, kind="png")
        buff.seek(0)
        qr = buff
    else:
        qr = _qr.svg_data_uri()

    return qr


def generate_qr_codes_pdf(entries: list[str]) -> BytesIO:
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

    # Calculate the position to center the QR code
    qr_size = 400  # Size of the QR code
    x = (width - qr_size) / 2
    y = (height - qr_size) / 2

    for entry in entries:
        # Draw the QR code image from BytesIO
        qr_code = generate_qr_code(entry, as_file_buff=True)
        qr_image = ImageReader(qr_code)
        c.drawImage(qr_image, x, y, width=qr_size, height=qr_size)

        # Set the font size for the URL text
        font_size = 24
        c.setFont("Helvetica", font_size)

        # Calculate the position to center the text
        text_width = c.stringWidth(f"{entry}", "Helvetica", font_size)
        text_x = (width - text_width) / 2

        # Add the URL text below the QR code
        c.drawString(text_x, y - 30, f"{entry}")

        # Create a new page for the next QR code
        c.showPage()

    c.save()
    pdf_io.seek(0)

    return pdf_io
