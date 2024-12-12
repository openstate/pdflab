FROM python:3.10-bookworm

RUN apt-get update && apt-get install -y build-essential libpoppler-cpp-dev \
        pkg-config python-dev-is-python3 ffmpeg libsm6 libxext6 vim \
        tesseract-ocr libtesseract-dev libleptonica-dev pkg-config tesseract-ocr-nld

RUN pip install --no-cache-dir pdftotext==2.1.4 pymupdf4llm==0.0.17 opencv-python tesserocr
# numpy required before installing torch
RUN pip install --no-cache-dir numpy==2.1.1
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
RUN pip install --no-cache-dir marker-pdf==1.0.2
RUN pip install --no-cache-dir docling

ENV TESSDATA_PREFIX='/usr/share/tesseract-ocr/5/tessdata/'

COPY lab /opt/ori/lab

WORKDIR /opt/ori/lab
