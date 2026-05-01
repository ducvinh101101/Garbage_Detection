import sys
import streamlit.runtime as st_runtime

if __name__ == "__main__":
    if not st_runtime.exists():
        from streamlit.web.cli import main as st_main
        sys.argv = ["streamlit", "run", __file__]
        sys.exit(st_main())

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from agent_core import tim_kiem_tai_che
import os

# Cấu hình trang Streamlit
st.set_page_config(page_title="Trợ lý Tái chế Thông minh", page_icon="♻️", layout="centered")

st.markdown("""
<style>
    .main {
        background-color: #f0f8f1;
    }
    .stTextInput input {
        border-radius: 10px;
    }
    .stButton button {
        border-radius: 10px;
        background-color: #4CAF50;
        color: white;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 20px;
        margin-bottom: 10px;
        display: inline-block;
        max-width: 80%;
    }
    .user-bubble {
        background-color: #e0f7fa;
        color: #006064;
        align-self: flex-end;
    }
    .ai-bubble {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #c8e6c9;
    }
</style>
""", unsafe_allow_html=True)

st.title("♻️ Trợ lý Tái chế Thông minh")
st.write("Hỏi tôi bất cứ điều gì về cách phân loại, tái chế rác hoặc quy định pháp luật về môi trường!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Lấy API Key
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    st.warning("Bạn chưa cấu hình GOOGLE_API_KEY trong biến môi trường.")
    api_key = st.text_input("Vui lòng nhập Google API Key của bạn để sử dụng Chatbot:", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        st.success("Đã lưu API Key tạm thời!")
        st.rerun()
    else:
        st.stop()

@st.cache_resource
def get_agent():
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    tools = [tim_kiem_tai_che]
    sys_msg = (
        "Bạn là một AI chuyên gia về môi trường và tái chế rác thải tại Việt Nam. "
        "Hãy luôn sử dụng công cụ `tim_kiem_tai_che` để tra cứu các thông tin về luật, quy định, "
        "cách xử lý các loại rác và địa điểm thu gom để có thông tin chính xác từ hệ thống RAG. "
        "Luôn trả lời thân thiện, rõ ràng, và dễ hiểu. Dùng định dạng markdown để trình bày đẹp mắt."
    )
    return create_react_agent(llm, tools, prompt=sys_msg)

agent_executor = get_agent()

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            st.write(msg.content)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.write(msg.content)

# Ô nhập liệu
if prompt := st.chat_input("Ví dụ: Cách xử lý chai nhựa HDPE thế nào?"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user", avatar="👤"):
        st.write(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Đang tra cứu dữ liệu và suy nghĩ..."):
            try:
                # Chỉ lấy 10 tin nhắn gần nhất để tránh quá tải context
                history = st.session_state.messages[-10:]
                
                result = agent_executor.invoke({"messages": history})
                answer = result["messages"][-1].content
                
                st.write(answer)
                st.session_state.messages.append(AIMessage(content=answer))
            except Exception as e:
                st.error(f"Đã xảy ra lỗi khi kết nối tới AI: {str(e)}")

