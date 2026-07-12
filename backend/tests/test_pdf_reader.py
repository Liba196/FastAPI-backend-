from app.services.pdf_reader import extract_pages

pages = extract_pages("documents/sample.pdf")

print(repr(pages[0]["text"]))