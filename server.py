from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from models import  prompt
from phi.tools.googlesearch import GoogleSearch

# Load environment variables from .env file
load_dotenv()
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/health")
async def health():
    return {"result": "Healthy Server!"}

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

# Create agent team
agent_team = Agent(
    model=OpenAIChat(
        id = "gpt-4o",
        temperature = 1,
        timeout = 30
    ),
   name="Agent Team",
   team=[self_intro_agent, analysis_project_agent,search_agent],
   add_history_to_messages=True,
   num_history_responses=3,
   show_tool_calls=False,
   tool_call_limit=1
)

@app.post("/prompt")
async def prompt(prompt: prompt):
    response = agent_team.run(f"{prompt.message}", stream=False)
    # 尋找 assistant role 的最後一條訊息
    assistant_content = None
    for message in response.messages:
        if message.role == "assistant" and message.content:
            assistant_content = message.content

    return {"result": True, "message": assistant_content}
