import pymupdf.layout
import pymupdf
import pymupdf4llm


doc = pymupdf.open('file.pdf')
md = pymupdf4llm.to_markdown(doc)