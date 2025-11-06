## Requirements:

1. FastAPI and Uvicorn

```bash
pip install fastapi uvicorn
```

2. Python Multipart

```bash
pip install python-multipart
```

3. EasyOCR Required Packages:

```bash
pip install easyocr
pip install pdf2image
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

4. Poppler utils:

```bash
# On Ubuntu/Debian:
sudo apt-get install poppler-utils
```

5. Ghostscript _(Must be installed in path)_

## Running the dev server

```bash
uvicorn main:app --reload
```
