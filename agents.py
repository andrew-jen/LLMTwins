from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from models import  prompt
from phi.tools.googlesearch import GoogleSearch
def self_introduction():
    return "我的名字叫做小明，我是一個 AI 聊天機器人，我可以幫助你進行自我介紹。"

self_intro_agent = Agent(
   name="Self-introduction Agent",
   role="自我介紹",
   tools=[self_introduction],
   show_tool_calls=True
)

def analyse_project():
    return "我是專案分析 Agent，我可以幫助你分析專案。"

analysis_project_agent = Agent(
   name="Project analysis Agent",
   role= "專案分析",
   tools=[analyse_project],
   show_tool_calls=True
)

def google_search():
    return '我是網路搜尋專家'

search_agent = Agent(
    model=OpenAIChat(id="gpt-4"),
    tools=[GoogleSearch()],
    description="You are a news agent that helps users find the latest news.",
    instructions=[
        "Given a topic by the user, respond with 4 latest news items about that topic.",
        "Search for 10 news items and select the top 4 unique items.",
        "Search in English and in French.",
    ],
    show_tool_calls=True,
    debug_mode=True,
)

agents_dict = {
    "self_intro_agent": self_intro_agent,
    "analysis_project_agent": analysis_project_agent,
    "search_agent": search_agent,
}