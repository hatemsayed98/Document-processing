from PyPDF2 import PdfReader
import PyPDF2




def get_num_pdf_pages(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        return num_pages
    except Exception as e:
        print(f"Error occurred while counting pages: {str(e)}")
        return None

def is_pdf(file):
    if file == "pdf":
        return True
    return False


def is_image(file):
    if file in ["jpg", "jpeg", "png", "gif"]:
        return True
    return False
