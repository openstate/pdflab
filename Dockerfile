FROM python:3.10-bookworm

RUN apt-get update && apt-get install -y build-essential libpoppler-cpp-dev \
        pkg-config python-dev-is-python3 ffmpeg libsm6 libxext6 vim \
        tesseract-ocr libtesseract-dev libleptonica-dev pkg-config tesseract-ocr-nld \
        poppler-utils

RUN pip install --no-cache-dir pdftotext==2.1.4 pymupdf4llm==0.0.17 pymupdf==1.25.1 opencv-python tesserocr
# RUN pip install --no-cache-dir pdftotext==2.1.4 pymupdf==1.25.1 opencv-python tesserocr
# RUN pip install git+https://github.com/HDembinski/pymupdf4llm.git@fast_image_merge#subdirectory=pymupdf4llm
# RUN pip install --no-cache-dir PyPDF2==1.27.12
RUN pip install --no-cache-dir PyPDF2==3.0.1
# numpy required before installing torch
RUN pip install --no-cache-dir numpy==2.1.1
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
RUN pip install --no-cache-dir marker-pdf==1.0.2
RUN pip install --no-cache-dir docling
RUN pip install --no-cache-dir "unstructured-ingest[pdf,markdown]"

ENV TESSDATA_PREFIX='/usr/share/tesseract-ocr/5/tessdata/'

COPY lab /opt/ori/lab

WORKDIR /opt/ori/lab
