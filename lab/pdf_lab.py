#"""
# Usage:
#   - docker build  --tag 'pdflab' .
#   - docker run --name pdflab -it pdflab bash
#       - python pdf_lab.py
# """
import time
import subprocess
import sys

import pdftotext
import pymupdf.layout # NOTE: by importing pymupdf.layout before pymupdf4llm this new way of parsing is used
import pymupdf4llm
import pymupdf
# from PyPDF2 import PdfFileReader # 1.27.12
# from PyPDF2.utils import PdfReadError # 1.27.12
from PyPDF2 import PdfReader # 3.0.1
from PyPDF2.errors import PdfReadError # 3.0.1
from pypdf import PdfReader as PypdfPdfReader # 5.5.0
from pypdf.errors import PyPdfError
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

            result_name = f'{fname}-pdftotext.txt'
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
                # reader = PdfFileReader(f) # 1.27.12
                reader = PdfReader(f)
                # text = ' '.join([p.extractText() for p in reader.pages]) # 1.27.12
                # text = ' '.join([p.extract_text() for p in reader.pages])
                text = [p.extract_text() for p in reader.pages]
            except PdfReadError as e:
                print(str(e))


            print("Processed %i pages" % len(reader.pages))

            result_name = f'{fname}-pypdf2.txt'
            out_file = open(result_name, 'w')
            for page in text:
                out_file.write(page)
            out_file.close()

class PyPDFLab():
    def convert(self, fname):
        print("\nConvert using PyPDF")
        pdf_name = f'{fname}.pdf'
        with open(pdf_name, "rb") as f:
            try:
                reader = PypdfPdfReader(f)
                text = [p.extract_text() for p in reader.pages]
            except PyPdfError as e:
                print(str(e))


            print("Processed %i pages" % len(reader.pages))

            result_name = f'{fname}-pypdf.txt'
            out_file = open(result_name, 'w')
            for page in text:
                out_file.write(page)
            out_file.close()

class PymuPdfLab():
    def convert(self, fname):
        print("\nConvert using pymupdf")
        pdf_name = f'{fname}.pdf'
        doc=pymupdf.open(pdf_name)
        texts = []
        for page in doc:
            texts.append(page.get_text())

        result_name = f'{fname}-pymupdf.txt'
        out_file = open(result_name, 'w')
        for page in texts:
            out_file.write(page)
        out_file.close()

class PymuPdf4LLMLab():
    def convert(self, fname, use_tesseract = False):
        pdf_name = f'{fname}.pdf'
        doc=pymupdf.open(pdf_name)
        # hdr=pymupdf4llm.IdentifyHeaders(doc)
        if use_tesseract:
            print("\nConvert using pymupdf4llm with tesseract ocr")
            md_text = []
            for index, page in enumerate(doc):
                print(f"parsing page {index}")
                pixmap = page.get_pixmap(dpi=200)
                doc=pymupdf.open("pdf", pixmap.pdfocr_tobytes(language='nld'))

                md_text.append(pymupdf4llm.to_markdown(doc, hdr_info=hdr, image_size_limit=0.1))
            result_name = f'{fname}-pymupdf4llm-tesseract.md'
        else:
            print("\nConvert using pymupdf4llm")
            md_chunks = pymupdf4llm.to_markdown(doc)
            # md_chunks = pymupdf4llm.to_markdown(pdf_name, hdr_info=hdr, page_chunks=True, show_progress=False,
            #                                     image_size_limit=0.1)
            # md_chunks = pymupdf4llm.to_markdown(pdf_name, hdr_info=hdr, page_chunks=True, show_progress=True,
            #                                     image_size_limit=0.1,
            #                                     ignore_graphics=True, ignore_images=True)
            
            md_text = [chunk['text'] for chunk in md_chunks]
            result_name = f'{fname}-pymupdf4llm.md'

        out_file = open(result_name, 'w')
        for page in md_text:
            out_file.write(page)
        out_file.close()

    # This method is used in open-raadinformatie to decide early on to use OCR or not
    def force_ocr(self, fname):
        pdf_name = f'{fname}.pdf'
        textflags = ( # definition taken from pymupdf4llm
            0
            | 64 # mupdf.FZ_STEXT_CLIP
            | 512 # mupdf.FZ_STEXT_ACCURATE_BBOXES
            # | mupdf.FZ_STEXT_IGNORE_ACTUALTEXT
            | 32768  # mupdf.FZ_STEXT_COLLECT_STYLES
        )

        try:
            with pymupdf.open(pdf_name) as doc: 
                i = 0
                for page in doc.pages():
                    i += 1
                    print(f"Processing page {i}")
                    textpage = page.get_textpage(flags=textflags, clip=page.rect)
                    blocks = textpage.extractDICT()["blocks"]
                    if len(blocks) > 150:
                        return True
        except Exception as e:
            print(f"Generic error occurred when getting number of bboxes in pdf, error is {e}")

        return False

    def get_images(self, fname):
        pdf_name = f'{fname}.pdf'
        try:
            rewrite = False
            with pymupdf.open(pdf_name) as doc: 
                for index, page in enumerate(doc.pages()):
                    print(f"\npage {index}")
                    number_of_images = len(page.get_images())
                    if number_of_images > 100:
                        print(f"PDF contains many image objects on a page ({number_of_images}), will be rewritten")
                        rewrite = True
                        break
            print(f"\nRewrite: {rewrite}")
        except:
            print(f"Generic error occurred when checking number of pages in pdf, error class is {sys.exc_info()[0]}, {sys.exc_info()[1]}")
            return

class PymuPdf4LLMUseTextpageOCRLab():
    def convert(self, fname):
        pdf_name = f'{fname}.pdf'
        doc=pymupdf.open(pdf_name)

        print("\nConvert using pymupdf4llm using get_textpage_ocr")
        md_text = []
        for index, page in enumerate(doc):
            print(f"parsing page {index}")
            text_page = page.get_textpage_ocr(flags=pymupdf.TEXTFLAGS_SEARCH, language='nld', full=False)
            text = page.get_text(textpage=text_page)
            md_text.append(text)

        result_name = f'{fname}-pymupdf4llm-gettextpageocr.md'
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
    
class OCRmyPDFLab():
    def convert(self, fname):
        print("\nConvert using OCRmyPDF")
        pdf_name = f'{fname}.pdf'
        out_file = f'{fname}-ocrmypdf.pdf'

        command = [
            'ocrmypdf',
            '--redo-ocr',
            '-l',
            'nld',
            pdf_name,
            out_file
        ]
        result = subprocess.run(command, capture_output=True)
        print(f"result code {result.returncode} {result.returncode.__class__.__name__}")
        print(f"result stdout {result.stdout}")
        print(f"result stderr {result.stderr}")



fname1 = 'motie'
fname2 = 'besluitenlijst'
fname3 = 'emmen_rekenkamercommissie'
fname4 = 'overijssel_jaarstukken_2023'
fname5 = 'toezeggingen_commissie_bme'
fname6 = 'besluitenlijst-ministerraad-20250110'
fname7 = 'Papendrecht-problem'
fname8 = '1848-scan'
fname9 = "Motie-528709"
fname10 = "Beslisnota-met-handgeschreven-tekst"
fname11 = "1848-notificatie-met-undefined-unicodes"
fname12 = "transporterror"
fname13 = "notubiz_645542_2"
fname14 = "almere_groot_bestand"
fname15 = "almere_bundel_LARGE"
fname16 = "amsterdam-2514pages"
# fname17 = "amsterdam-2514pages-rewritten"
fname18 = "index_error-rewritten"
fname19 = "celery_worker_lost"
fname20 = "1848_ic"
fname21 = "ic_no_ocr"
fname22 = "19 Geurgebiedsvisie 2013 - met bijlagen DEF"
fname23 = "Bijlagenboek bij toelichting BP Korte Heistraat 2-4"
fname24 = "7986398_02 Bijlage A bij ontwerp raadsbesluit"
fname25 = "3.1 Besluitdocument_Renvooi Huidig-Definitief OP Bodem en basisstructuur"
fname26 = "file" # BESTEMMINGSPLAN BOEKELERMEER NOORD

fname = fname26
fnames = [fname1, fname2, fname3, fname4, fname5, fname6, fname7, fname8, fname9, fname10, fname11, fname12, fname13, fname14, fname15]

# current_time = time.process_time()
# PdfToTextLab().convert(fname)
# print(f"Took {time.process_time() - current_time} seconds")

# current_time = time.process_time()
# PymuPdfLab().convert(fname)
# print(f"Took {time.process_time() - current_time} seconds")

current_time = time.process_time()
# PymuPdf4LLMLab().convert(fname)
# force_ocr = PymuPdf4LLMLab().force_ocr(fname)
# print(f"force_ocr: {force_ocr}")
PymuPdf4LLMLab().convert(fname, False)
# PymuPdf4LLMUseTextpageOCRLab().convert(fname)
# PymuPdf4LLMLab().get_images(fname)
print(f"Took {time.process_time() - current_time} seconds")

# current_time = time.process_time()
# PyPDF2Lab().convert(fname)
# print(f"Took {time.process_time() - current_time} seconds")

# current_time = time.process_time()
# PyPDFLab().convert(fname)
# print(f"Took {time.process_time() - current_time} seconds")

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

# current_time = time.process_time()
# OCRmyPDFLab().convert(fname)
# print(f"Took {time.process_time() - current_time} seconds")
