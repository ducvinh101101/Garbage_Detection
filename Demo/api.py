import os
import base64
import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

# Import tools from agent_core
from agent_core import tim_kiem_tai_che, tim_kiem_internet

app = FastAPI(title="Smart Recycling AI Backend")

# Phục vụ thư mục frontend (HTML/CSS/JS)
# Cần tạo thư mục 'frontend' và các file tương ứng
if not os.path.exists("frontend"):
    os.makedirs("frontend")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

class Message(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    history: List[Message]
    prompt: str
    api_key: Optional[str] = None # Nhận API Key từ Frontend thay vì yêu cầu biến môi trường cứng
    image: Optional[str] = None # Ảnh base64

def get_agent(api_key: str):
    if not api_key:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp Google API Key.")
    
    # Thiết lập biến môi trường tạm thời cho Langchain
    os.environ["GOOGLE_API_KEY"] = api_key
    
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        tools = [tim_kiem_tai_che, tim_kiem_internet]
        sys_msg = (
            "Bạn là một AI chuyên gia về môi trường và tái chế rác thải tại Việt Nam. "
            "1. Hãy luôn ưu tiên sử dụng công cụ `tim_kiem_tai_che` để tra cứu các thông tin về luật, quy định, cách xử lý từ hệ thống RAG nội bộ trước. "
            "2. Nếu tài liệu nội bộ không có đủ thông tin hoặc cần lấy Top 3 tài liệu tốt nhất tham khảo trên internet, hãy dùng công cụ `tim_kiem_internet`. "
            "Luôn trả lời thân thiện, rõ ràng, và dễ hiểu. Dùng định dạng markdown để trình bày đẹp mắt và chèn đường link tham khảo nếu có."
        )
        return create_react_agent(llm, tools, prompt=sys_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khởi tạo AI: {str(e)}")

@app.get("/")
def read_root():
    return FileResponse("frontend/index.html")

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    agent_executor = get_agent(req.api_key)
    
    extra_prompt = ""
    if req.image:
        try:
            # Decode base64 image
            if "," in req.image:
                base64_data = req.image.split(",")[1]
            else:
                base64_data = req.image
                
            image_bytes = base64.b64decode(base64_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is not None:
                from agent_core import plastic_model, plastic_class_names
                from tensorflow.keras.applications.vgg16 import preprocess_input
                
                if plastic_model is not None:
                    # Tiền xử lý ảnh giống mô hình
                    img_resized = cv2.resize(img, (224, 224))
                    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
                    img_array = np.expand_dims(img_rgb, axis=0)
                    img_array = preprocess_input(img_array.astype(np.float32))
                    
                    preds = plastic_model.predict(img_array, verbose=0)
                    class_idx = int(np.argmax(preds[0]))
                    class_name = plastic_class_names.get(class_idx, "Không xác định")
                    extra_prompt = f"Camera AI đã phân tích món đồ này trong ảnh là nhựa loại: {class_name}. "
                    print(f"[Backend] Đã nhận diện nhựa: {class_name}")
                else:
                    print("[Backend] Lỗi: Chưa tải được mô hình phân loại nhựa.")
        except Exception as e:
            print(f"[Backend] Lỗi xử lý ảnh: {e}")

    full_prompt = req.prompt
    if extra_prompt:
        if not full_prompt.strip():
            full_prompt = f"{extra_prompt}Hãy tìm hướng dẫn tái chế cho tôi."
        else:
            full_prompt = f"{extra_prompt}{full_prompt}"
            
    # Chuyển đổi lịch sử
    messages = []
    # Chỉ lấy 10 tin nhắn gần nhất để tránh tràn bộ nhớ context
    for msg in req.history[-10:]:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))
            
    # Thêm prompt hiện tại
    messages.append(HumanMessage(content=full_prompt))
    
    try:
        result = agent_executor.invoke({"messages": messages})
        answer = result["messages"][-1].content
        
        # Xử lý trường hợp Gemini trả về list thay vì chuỗi string
        if isinstance(answer, list):
            text_parts = []
            for item in answer:
                if isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
                elif isinstance(item, str):
                    text_parts.append(item)
            answer = "".join(text_parts)
            
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
