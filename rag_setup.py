# rag_setup.py
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def build_vector_db():
    print("Đang đọc tài liệu và tạo Vector DB...")
    # 1. Load tài liệu
    loader = TextLoader("tai_lieu_tai_che.txt", encoding="utf-8")
    docs = loader.load()

    # 2. Cắt nhỏ tài liệu
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)

    # 3. Dùng mô hình nhúng (Embeddings) miễn phí của HuggingFace
    embeddings = HuggingFaceEmbeddings(model_name="keepitreal/vietnamese-sbert")

    # 4. Lưu vào ChromaDB
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory="./chroma_db")
    print("Đã tạo xong Vector DB!")

if __name__ == "__main__":
    build_vector_db()