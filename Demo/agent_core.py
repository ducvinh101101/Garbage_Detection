import os
import cv2
import base64
import json
import numpy as np
from typing import Optional, Type, Dict, Any

from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input

# Khởi tạo mô hình phân loại nhựa
try:
    plastic_model = load_model("plastic/plastic_classification.keras")
    with open("plastic/class_indices.json", "r") as f:
        class_indices = json.load(f)
        plastic_class_names = {v: k for k, v in class_indices.items()}
except Exception as e:
    print(f"Cảnh báo: Lỗi tải mô hình phân loại nhựa cục bộ: {e}")
    plastic_model = None
    plastic_class_names = {}

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage

# Khởi tạo DB RAG đã được lưu trữ (chỉ thực hiện khi DB đã được tạo)
try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    retriever = vectorstore.as_retriever()
except Exception as e:
    print(f"Cảnh báo: Chưa thể tải vector database (lỗi: {e}). Hãy chạy rag_setup.py trước.")
    retriever = None

@tool
def tim_kiem_tai_che(query: str) -> str:
    """
    Sử dụng công cụ này để tìm kiếm thông tin RAG về cách xử lý hoặc địa điểm thu gom một loại rác cụ thể.
    Ví dụ query: 'Cách xử lý nhựa PET' hoặc 'Địa điểm thu gom HDPE'.
    """
    if retriever:
        docs = retriever.invoke(query)
        if not docs:
            return "Không tìm thấy thông tin phù hợp trong CSDL."
        return "\n".join([doc.page_content for doc in docs])
    return "Chưa khởi tạo Database RAG."

@tool
def tim_kiem_internet(query: str) -> str:
    """
    Sử dụng công cụ này để tìm kiếm trên Internet các thông tin mới nhất và Top 3 tài liệu tốt nhất về cách tái chế khi không tìm thấy trong cơ sở dữ liệu nội bộ.
    """
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=3)
        if not results:
            return "Không tìm thấy kết quả nào trên internet."
        
        response = "Dưới đây là Top 3 tài liệu hữu ích từ Internet:\n"
        for i, r in enumerate(results, 1):
            response += f"{i}. [{r['title']}]({r['href']})\n"
        return response
    except Exception as e:
        return f"Lỗi khi tìm kiếm trên internet: {e}"

def run_agent_pipeline(image_crop):
    print("\n[AI AGENT] Bắt đầu suy luận với LangChain...")
    
    if os.environ.get("GOOGLE_API_KEY") is None:
        print("Vui lòng thiết lập biến môi trường GOOGLE_API_KEY trước khi chạy AI Agent.")
        return "Lỗi cấu hình AI Agent."

    # 1. Thực hiện phân loại nhựa bằng model cục bộ (Keras) ngay tại đây
    class_name = "Không xác định"
    if plastic_model is not None:
        try:
            # Tiền xử lý giống hệt mô hình phân loại rác ban đầu (resize và preprocess của vgg16)
            img = cv2.resize(image_crop, (224, 224))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_array = np.expand_dims(img, axis=0)
            img_array = preprocess_input(img_array.astype(np.float32))
            
            preds = plastic_model.predict(img_array, verbose=0)
            class_idx = int(np.argmax(preds[0]))
            class_name = plastic_class_names.get(class_idx, "Không xác định")
            print(f"-> [Thị giác máy tính] Đã nhận diện loại nhựa: {class_name}")
        except Exception as e:
            print(f"-> [Lỗi] Không thể phân loại nhựa: {e}")
    else:
        print("-> [Lỗi] Chưa tải được mô hình phân loại nhựa cục bộ.")
    
    # 2. Khởi tạo danh sách các Tool
    tools = [tim_kiem_tai_che, tim_kiem_internet]
    
    # 3. Khởi tạo LLM ("bộ não") sẽ đưa ra quyết định
    # Sử dụng 'gemini-2.5-flash' để phản hồi nhanh và gọi tool tốt
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    # 4. Định nghĩa luồng suy nghĩ của Agent
    sys_msg = (
        "Bạn là một AI chuyên gia tái chế rác thải thông minh. "
        "Hệ thống Camera đã nhận diện loại nhựa của đồ vật. "
        "Nhiệm vụ của bạn là: \n"
        "1. Ưu tiên sử dụng công cụ `tim_kiem_tai_che` để tìm kiếm thông tin trong Cơ sở dữ liệu RAG nội bộ trước.\n"
        "2. Nếu tài liệu nội bộ không cung cấp đủ thông tin, HÃY SỬ DỤNG công cụ `tim_kiem_internet` để lấy top 3 nguồn tài liệu tốt nhất từ internet.\n"
        "3. Tổng hợp lại thành một câu trả lời duy nhất thật tự nhiên để hướng dẫn cho người dùng, bao gồm cả cách xử lý và trích dẫn các đường link tài liệu nếu có."
    )
    
    # Tạo agent
    agent_executor = create_react_agent(llm, tools, prompt=sys_msg)
    
    try:
        # Gửi thẳng tên loại nhựa (Text) vào prompt, siêu nhẹ và nhanh!
        result = agent_executor.invoke({
            "messages": [("user", f"Camera AI đã phân tích món đồ này là nhựa loại: {class_name}. Hãy tìm hướng dẫn tái chế cho tôi và đính kèm 3 tài liệu tham khảo tốt nhất trên internet.")]
        })
        
        final_answer = result["messages"][-1].content
        print("\n=== KẾT QUẢ TỪ AI AGENT ===")
        print(final_answer)
        print("=============================\n")
        return final_answer
        
    except Exception as e:
        print(f"Lỗi khi chạy Agent: {e}")
        return "Xin lỗi, không thể kết nối tới não bộ AI ngay lúc này."