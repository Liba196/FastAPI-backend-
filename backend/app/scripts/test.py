from ingest import extract_text
pages = extract_text("documents/sample2.pdf")
for p in pages[:3]:
    print(p["page_number"], "-> chars extracted:", len(p["text"]))