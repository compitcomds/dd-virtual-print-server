import os

def get_ps_path(file_id: str, make_ps_folder=False):
    if make_ps_folder:
        os.makedirs("ps", exist_ok=True)
    path = os.path.join("ps", f"{file_id}.ps")
    return path

def get_pdf_path(file_id: str, make_pdf_folder=False):
    if make_pdf_folder:
        os.makedirs("pdf", exist_ok=True)

    path = os.path.join("pdf", f"{file_id}.pdf")
    return path