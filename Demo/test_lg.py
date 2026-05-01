from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
import os

print("Imports ok!")
@tool
def dummy():
    """hello"""
    pass

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
try:
    agent = create_react_agent(llm, tools=[dummy])
    print("Agent created ok!")
except Exception as e:
    print("Error:", e)
