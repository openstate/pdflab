#"""
# Usage:
#   - docker build  --tag 'pdflab' .
#   - docker run --name pdflab -it pdflab bash
#       - time python pdf_lab.py
# """
import pdftotext
import pymupdf4llm
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption

class PdfToTextLab():
    def convert(self, fname):
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
        pdf_name = f'{fname}.pdf'
        md_text = pymupdf4llm.to_markdown(pdf_name)

        result_name = f'{fname}-pymupdf4llm.md'
        out_file = open(result_name, 'w')
        out_file.write(md_text)
        out_file.close()

class MarkerLab():
    def convert(self, fname):
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
            print("Using tesseract ocr")
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr=True
            pipeline_options.ocr_options = TesseractOcrOptions()
            doc_converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
        else:
            doc_converter = DocumentConverter()
        result = doc_converter.convert(pdf_name)

        result_name = f'{fname}-docling-tesseract.md'
        out_file = open(result_name, 'w')
        out_file.write(result.document.export_to_markdown())
        out_file.close()



fname1 = 'motie'
fname2 = 'besluitenlijst'
fname3 = 'example1'

# lab = PdfToTextLab()
# lab = PymuPdf4LLMLab()
# lab = MarkerLab()
lab = DoclingLab()
lab.convert(fname1)
