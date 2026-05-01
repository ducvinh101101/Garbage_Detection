# agent_core.py
import os
import base64
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# ĐIỀN API KEY CỦA BẠN VÀO ĐÂY
os.environ["GOOGLE_API_KEY"] = "AIzaSy_YOUR_GEMINI_API_KEY_HERE"

# Load lại VectorDB đã tạo ở Bước 1
embeddings = HuggingFaceEmbeddings(model_name="keepitreal/vietnamese-sbert")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})


# ==========================================
# TOOL 1: CÔNG CỤ TRA CỨU RAG
# ==========================================
@tool
def get_recycling_guidelines(query: str) -> str:
    """
    Sử dụng công cụ này khi cần tìm kiếm hướng dẫn tái chế, cách xử lý rác
    và địa điểm thu gom cho một loại rác cụ thể (VD: Nhựa PET, Nhựa HDPE...).
    """
    docs = retriever.invoke(query)
    info = "\n".join([doc.page_content for doc in docs])
    return info if info else "Không tìm thấy thông tin tái chế trong cơ sở dữ liệu."


# ==========================================
# TOOL 2: CÔNG CỤ NHÌN ẢNH (VISION)
# ==========================================
@tool
def analyze_plastic_image(image_path: str) -> str:
    """
    Sử dụng công cụ này để phân tích hình ảnh cận cảnh của đồ nhựa.
    Input là đường dẫn file ảnh. Output là loại nhựa (PET, HDPE, PVC...).
    """
    # Khởi tạo mô hình Gemini Vision
    vision_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    # Đọc ảnh chuyển sang base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    prompt = "Đây là một món đồ nhựa. Hãy cho tôi biết khả năng cao nhất nó là loại nhựa gì (PET, HDPE, PP, v.v.). Chỉ cần trả về tên loại nhựa ngắn gọn."

    # Gửi ảnh cho Gemini phán đoán
    message = vision_llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_string}"}}
            ]
        }
    ])
    return message.content



# Tổng hợp các tools
tools = [get_recycling_guidelines, analyze_plastic_image]

# Khởi tạo LLM chính chỉ đạo Agent
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

# Viết Prompt hướng dẫn Agent cách làm việc
prompt = ChatPromptTemplate.from_messages([
    ("system", "Bạn là chuyên gia tư vấn môi trường. Khi người dùng gửi đường dẫn ảnh rác nhựa, bạn phải làm theo thứ tự: "
               "1. Dùng tool 'analyze_plastic_image' để xem đó là nhựa gì. "
               "2. Dùng tool 'get_recycling_guidelines' để tìm cách tái chế và địa điểm thu gom. "
               "3. Trả lời người dùng bằng tiếng Việt, thân thiện và rõ ràng."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Tạo Agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def run_agent_pipeline(image_path: str):
    """Hàm này sẽ được gọi từ bên file OpenCV"""
    print("Agent đang suy nghĩ...")
    response = agent_executor.invoke({"input": f"Hãy phân tích ảnh tại đường dẫn này: {image_path} và cho tôi lời khuyên tái chế."})
    return response["output"]