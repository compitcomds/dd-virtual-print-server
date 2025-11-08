import uuid, os, asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse, JSONResponse, FileResponse
from src.utils import get_ps_path
from src.process_ps_files_loop import process_ps_files_loop
from db import init_db, get_file_record, update_file_record, add_file_record
import hashlib

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()
    asyncio.create_task(process_ps_files_loop())

@app.get("/", response_class=PlainTextResponse)
def hello():
    return "Server is up and running"

@app.post("/upload-ps")
async def upload_ps(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".ps"):
        return JSONResponse({"error": "Only .ps files allowed"}, status_code=400)

    content = await file.read()
    file_id = str(uuid.uuid4())
    ps_path = store_ps_file(file_id, content)
    add_file_record(file_id, ps_path)
    return {"file_id": file_id, "status": "uploaded"}

@app.get("/download/{file_id}")
def download_pdf(file_id: str, background_tasks: BackgroundTasks):
    record = get_file_record(file_id)

    if not record:
        raise HTTPException(status_code=404, detail="File id not found")

    pdf_path = record["pdf_path"]
    ps_path = record["ps_path"]
    status = record["status"]
    certificate_id = record["certificate_id"]
    log_message = record["log_message"]

    if status == "downloaded":
        raise HTTPException(status_code=400, detail="The file is already downloaded.")

    if certificate_id and os.path.exists(pdf_path):
        background_tasks.add_task(remove_file, file_id, ps_path, pdf_path)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{certificate_id}.pdf",
            background=background_tasks
        )

    if status == "failed":
        raise HTTPException(status_code=400, detail=log_message or "The extraction for the file failed.")
    
    return JSONResponse({"status": status, "message": "The file will start processing soon." if status == "uploaded" else "The file is in processing"}, status_code=201)

def remove_file(file_id: str, ps_path: str, pdf_path: str):
    update_file_record(file_id, status="downloaded")
    os.remove(pdf_path)
    os.remove(ps_path)

def store_ps_file(file_id, content):
    path = get_ps_path(file_id, make_ps_folder=True)
    with open(path, "wb") as f:
        f.write(content)
    
    print("Uploaded hash:", hashlib.md5(content).hexdigest())
    return path
