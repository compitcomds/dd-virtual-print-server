import asyncio
from db import update_status, update_file_record, get_next_processing_record
from .utils import get_pdf_path
from .convert import convert_ps_to_pdf

async def process_ps_files_loop():
    loop = asyncio.get_running_loop()

    """Background service that continuously processes pending PS files."""
    while True:
        try:
            record = get_next_processing_record()
            if not record:
                raise Exception("No record found!")

            file_id = record["file_id"]
            ps_path = record["ps_path"]
            status = record["status"]

            print("Processing: ", file_id)

            pdf_path = record.get("pdf_path") or get_pdf_path(file_id, make_pdf_folder=True)

            print("PDF Path: ", pdf_path)

            if status == "uploaded":
                result, message = await loop.run_in_executor(None, convert_ps_to_pdf, ps_path, pdf_path)    
                if result:
                    update_status(file_id, "converted")
                else:
                    update_file_record(file_id, status="failed", log_message=message)
                    raise Exception(message)

        except Exception as e:
            print(e)
            await asyncio.sleep(5)
