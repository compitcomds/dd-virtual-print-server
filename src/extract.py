import easyocr, torch
from pdf2image import convert_from_path
import numpy as np
import re
from typing import Optional

class CertificateExtractor:
    def __init__(self):
        print("Initializing EasyOCR reader with GPU...")
        cuda_available = torch.cuda.is_available()
        print(f"CUDA Available: {cuda_available}")

        if cuda_available:
            print(f"CUDA Version: {torch.version.cuda}")
            gpu_count = torch.cuda.device_count()
            print(f"Number of GPUs: {gpu_count}")
            current_device = torch.cuda.current_device()
            print(f"Current GPU Index: {current_device}")

    
        self.reader = easyocr.Reader(['en'], gpu=True)
    
    def extract_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Extract certificate ID from PDF"""
        images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)
        image = images[0]

        print(f"Processing page...")
        img_array = np.array(image)
        results = self.reader.readtext(img_array)

        for (bbox, text, confidence) in results:
            match = re.search(r'IN-[A-Z0-9]+X', text, re.IGNORECASE)
            if match:
                return match.group(0).upper()
        
        return None

certificate_extractor = CertificateExtractor()
