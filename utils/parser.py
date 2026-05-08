import fitz


def extract_text_from_pdf(pdf_path):

    text = ""

    pdf_document = fitz.open(pdf_path)

    for page in pdf_document:

        text += page.get_text()

    return text