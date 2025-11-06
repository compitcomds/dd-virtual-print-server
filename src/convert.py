import os, subprocess
import shutil

gs_paths = [
    "gswin64c",
    "gswin32c",
    "gs"
]

gs_cmd = None

for gs_path in gs_paths:
    if shutil.which(gs_path):
        gs_cmd = gs_path
        break

if not gs_cmd:
    raise FileNotFoundError("Ghostscript not found in PATH")

def convert_ps_to_pdf(ps_file: str, pdf_file: str):
    try:
        print(f"Conversion for ps<{os.path.basename(ps_file)}> -> pdf<{os.path.basename(pdf_file)}>")

        if not os.path.exists(ps_file):
            print("PS File not found", ps_file)
            return False, f"PS File not found: {ps_file}"

        if not gs_cmd:
            print("Ghostscript not found", "error")
            return False, "Ghostscript not found"
        
        cmd = [
            gs_cmd,
            "-dNOPAUSE", "-dBATCH", "-dSAFER",
            "-sDEVICE=pdfwrite",
            f"-sOutputFile={pdf_file}",
            ps_file
        ]

        print("Converting ps file to pdf file")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0 and os.path.exists(pdf_file):
            return True, "Success"
        else:
            return False, result.stderr or "Conversion failed"

    except Exception as e:
        return False, str(e)