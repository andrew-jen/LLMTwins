from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from models import  prompt
from phi.tools.googlesearch import GoogleSearch
import agents

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


agent_instances = [agent for agent in agents.agents_dict.values()]

# Create agent team
agent_team = Agent(
    model=OpenAIChat(
        id="gpt-4o",
        temperature=1,
        timeout=30
    ),
    name="Agent Team",
    team=agent_instances,  # 使用动态加载的 Agent 实例
    add_history_to_messages=True,
    num_history_responses=3,
    show_tool_calls=False,
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
