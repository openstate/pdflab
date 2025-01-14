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
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Title, Text, NarrativeText

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

class PyPDF2Lab():
    def convert(self, fname):
        print("\nConvert using PyPDF2")
        pdf_name = f'{fname}.pdf'
        with open(pdf_name, "rb") as f:
            try:
                reader = PdfReader(f)
                text = ' '.join([p.extract_text() for p in reader.pages])
            except PdfReadError as e:
                print(str(e))


            print("Processed %i pages" % len(reader.pages))

            result_name = f'{fname}-pypdf2.md'
            out_file = open(result_name, 'w')
            out_file.write(text)
            out_file.close()

class PymuPdf4LLMLab():
    def convert(self, fname, use_tesseract = False):
        pdf_name = f'{fname}.pdf'
        doc=pymupdf.open(pdf_name)
        hdr=pymupdf4llm.IdentifyHeaders(doc)
        if use_tesseract:
            print("\nConvert using pymupdf4llm with tesseract ocr")
            md_text = []
            for page in doc:
                pixmap = page.get_pixmap(dpi=300)
                doc=pymupdf.open("pdf", pixmap.pdfocr_tobytes(language='nld'))

                md_text.append(pymupdf4llm.to_markdown(doc, hdr_info=hdr))
            result_name = f'{fname}-pymupdf4llm-tesseract.md'
        else:
            print("\nConvert using pymupdf4llm")
            md_chunks = pymupdf4llm.to_markdown(pdf_name, hdr_info=hdr, page_chunks=True, show_progress=False)
            md_text = [chunk['text'] for chunk in md_chunks]
            result_name = f'{fname}-pymupdf4llm.md'

        out_file = open(result_name, 'w')
        for page in md_text:
            out_file.write(page)
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

class UnstructuredLab():
    def convert(self, fname):
        print("\nConvert using unstructured")
        pdf_name = f'{fname}.pdf'
        elements = partition_pdf(pdf_name, strategy="hi_res")

        # unstructured currently does not have a markdown output option
        # Apart from that, tables are not parsed correctly.
        # convert_to_markdown was started to output markdown, but wasn't finished
        result_name = f'{fname}-unstructured.md'
        markdown_content = self.convert_to_markdown(elements)
        out_file = open(result_name, 'w')
        out_file.write(markdown_content)
        out_file.close()

    def convert_to_markdown(self, elements):
        data = [element.to_dict() for element in elements]
        markdown = ""
        
        for item in data:
            print(item)
            element_type = item['type']
            text = item['text']
            
            if element_type == 'Title':
                markdown += f"# {text}\n\n"
            elif element_type == 'Text':
                markdown += f"{text}\n\n"
            elif element_type == 'NarrativeText':
                markdown += f"{text}\n\n"
            else:
                print(f'Unknown element type: {item["type"]}')    
            
        return markdown.strip()
    
fname1 = 'motie'
fname2 = 'besluitenlijst'
fname3 = 'emmen_rekenkamercommissie'
fname4 = 'overijssel_jaarstukken_2023'
fname5 = 'toezeggingen_commissie_bme'
fname6 = 'besluitenlijst-ministerraad-20250110'

fname = fname6

current_time = time.process_time()
PdfToTextLab().convert(fname)
print(f"Took {time.process_time() - current_time} seconds")

current_time = time.process_time()
PymuPdf4LLMLab().convert(fname)
print(f"Took {time.process_time() - current_time} seconds")

current_time = time.process_time()
PyPDF2Lab().convert(fname)
print(f"Took {time.process_time() - current_time} seconds")

# current_time = time.process_time()
# MarkerLab().convert(fname)
# print(f"Took {time.process_time() - current_time} seconds")

# current_time = time.process_time()
# DoclingLab().convert(fname)
# print(f"Took {time.process_time() - current_time} seconds")

# current_time = time.process_time()
# DoclingLab().convert(fname, True)
# print(f"Took {time.process_time() - current_time} seconds")

# current_time = time.process_time()
# UnstructuredLab().convert(fname)
# print(f"Took {time.process_time() - current_time} seconds")
