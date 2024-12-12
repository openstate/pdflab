#"""
# Usage:
#   - docker build  --tag 'pdflab' .
#   - docker run --name pdflab -it pdflab bash
#       - python pdf_lab.py
# """
import time

import pdftotext
import pymupdf4llm
import pymupdf
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption

class PdfToTextLab():
    def convert(self, fname):
        print("\nConvert using pdftotext")
        pdf_name = f'{fname}.pdf'
        with open(pdf_name, "rb") as f:
            result_pages = []
            i = 0
            try:
                for i, page in enumerate(pdftotext.PDF(f), start=1):
                    result_pages.append(page)

            except pdftotext.Error as e:
                print(str(e))

            print("Processed %i pages" % i)

            result_name = f'{fname}-pdftotext.md'
            out_file = open(result_name, 'w')
            for page in result_pages:
                out_file.write(page)
            out_file.close()

class PymuPdf4LLMLab():
    def convert(self, fname):
        print("\nConvert using pymupdf4llm")
        pdf_name = f'{fname}.pdf'
        doc=pymupdf.open(pdf_name)
        hdr=pymupdf4llm.IdentifyHeaders(doc)
        print(hdr.header_id)
        md_text = pymupdf4llm.to_markdown(pdf_name, hdr_info=hdr)

        result_name = f'{fname}-pymupdf4llm.md'
        out_file = open(result_name, 'w')
        out_file.write(md_text)
        out_file.close()

class MarkerLab():
    def convert(self, fname):
        print("\nConvert using marker")
        pdf_name = f'{fname}.pdf'
        converter = PdfConverter(artifact_dict=create_model_dict())
        rendered = converter(pdf_name)
        text, _, images = text_from_rendered(rendered)

        result_name = f'{fname}-marker.md'
        out_file = open(result_name, 'w')
        out_file.write(text)
        out_file.close()

class DoclingLab():
    def convert(self, fname, use_tesseract = False):
        pdf_name = f'{fname}.pdf'
        if use_tesseract:
            print("\nConvert using docling with tesseract ocr")
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr=True
            pipeline_options.ocr_options = TesseractOcrOptions()
            doc_converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
            result_name = f'{fname}-docling-tesseract.md'
        else:
            print("\nConvert using docling with easyocr")
            doc_converter = DocumentConverter()
            result_name = f'{fname}-docling.md'

        result = doc_converter.convert(pdf_name)

        out_file = open(result_name, 'w')
        out_file.write(result.document.export_to_markdown())
        out_file.close()



fname1 = 'motie'
fname2 = 'besluitenlijst'
fname3 = 'emmen_rekenkamercommissie'
fname4 = 'overijssel_jaarstukken_2023'

fname = fname1

current_time = time.process_time()
PdfToTextLab().convert(fname)
print(f"Took {time.process_time() - current_time} seconds")

current_time = time.process_time()
PymuPdf4LLMLab().convert(fname)
print(f"Took {time.process_time() - current_time} seconds")

current_time = time.process_time()
MarkerLab().convert(fname)
print(f"Took {time.process_time() - current_time} seconds")

current_time = time.process_time()
DoclingLab().convert(fname)
print(f"Took {time.process_time() - current_time} seconds")

current_time = time.process_time()
DoclingLab().convert(fname, True)
print(f"Took {time.process_time() - current_time} seconds")
