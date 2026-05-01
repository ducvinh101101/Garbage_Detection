import os
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

def setup_rag_database():
    print("Đang khởi tạo Vector Database...")
    # 1. Load tài liệu
    try:
        loader = TextLoader("tai_lieu_tai_che.txt", encoding="utf-8")
        documents = loader.load()
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return

    # 2. Cắt nhỏ tài liệu
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    # 3. Dùng HuggingFace để tạo vector
    # Sử dụng model đa ngôn ngữ để hỗ trợ tiếng Việt hiệu quả
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    # 4. Lưu vào ChromaDB
    db_dir = "./chroma_db"
    
    vectorstore = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=db_dir
    )
    print(f"Đã lưu Database tại {db_dir}")

if __name__ == "__main__":
    setup_rag_database()