from fastapi import FastAPI, File, UploadFile
from fastapi.responses import PlainTextResponse, JSONResponse
import uuid, os
from src.utils import get_ps_path

app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
def hello():
    return "Server is up and running"

@app.post("/upload-ps")
async def upload_ps(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".ps"):
        return JSONResponse({"error": "Only .ps files allowed"}, status_code=400)

    content = await file.read()
    file_id = store_ps_file(content)

    return {"file_id": file_id, "status": "uploaded"}

def store_ps_file(content):
    file_id = str(uuid.uuid4())
    path = get_ps_path(file_id, make_ps_folder=True)
    with open(path, "wb") as f:
        f.write(content)
    return file_id
