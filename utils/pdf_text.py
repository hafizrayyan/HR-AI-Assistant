import pypdf

import re

def clean_text(text):
    # Remove extra blank lines
    text = re.sub(r'\n{2,}', '\n', text)

    # Remove extra spaces
    text = re.sub(r'[ \t]+', ' ', text)

    # Remove page numbers
    text = re.sub(r'Page \d+ of \d+', '', text)

    return text.strip()





def pdf_text_ext(pdf):

    text = ""
    read = pypdf.PdfReader(pdf)

    for page in read.pages: 
        content = page.extract_text()
        if content :
            text += content


    text = clean_text(text)
    return text 
    print("PDF Loaded Successfully")