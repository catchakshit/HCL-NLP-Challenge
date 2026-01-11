import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

PDF_PATH = "data/hcl.pdf"
DB_PATH = "index"

def load_pdf():
    doc = fitz.open(PDF_PATH)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "text": text,
            "page": i + 1
        })
    return pages

def main():
    pages = load_pdf()

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)

    texts = []
    metadatas = []

    for p in pages:
        chunks = splitter.split_text(p["text"])
        for c in chunks:
            texts.append(c)
            metadatas.append({"page": p["page"]})

    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    db = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
    db.save_local(DB_PATH)

    print("✅ Vector DB created successfully!")

if __name__ == "__main__":
    main()
