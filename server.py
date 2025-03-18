from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from models import prompt  # 確保這裡有對應的 prompt 類別
from phi.tools.googlesearch import GoogleSearch
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import agents  # 確保這裡有正確的代理人字典
from fastapi.security import OAuth2PasswordBearer

# 定义 OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
OpenAIChat(
    id="gpt-4o",
    temperature=1,
    timeout=30,
    api_key="請使用您的API Key"  # 这里传入 API Key
)

# Load environment variables from .env file
load_dotenv()

# Secret key and algorithm for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Simulated user database
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "password": "testpassword",
        "agent": ['self_intro_agent', 'search_agent']  # In a real application, passwords should be hashed
    },
    "sam": {
        "username": "sam",
        "password": "sampassword",
        "agent": ['self_intro_agent']
    },
    "andrew": {
        "username": "andrew",
        "password": "andrewpassword",
        "agent": ['search_agent']
    },
    "dino": {
        "username": "dino",
        "password": "dinopassword",
        "agent": ['self_intro_agent']
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str

class UserInDB(User):
    password: str

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_password(plain_password, stored_password):
    print(plain_password,stored_password)
    return plain_password == stored_password

def get_user(db, username: str):
    user = db.get(username)
    if user:
        return UserInDB(**user)

def authenticate_user(db, username: str, password: str):
    print(username)
    user = get_user(db, username)
    if not user or not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:  # 比對使用者輸入的帳密
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Health Check
@app.get("/health")
async def health():
    return {"result": "Healthy Server!"}

@app.post("/prompt")
async def prompt_endpoint(prompt: prompt, current_user: User = Depends(get_current_user)):
    # 获取当前用户的代理配置
    user_agents = fake_users_db[current_user.username]["agent"]
    print(user_agents)
    # 动态创建所需的 agent 实例
    agent_instances = [
        agent for name, agent in agents.agents_dict.items() if name in user_agents
    ]

    # 动态创建 agent team
    agent_team = Agent(
        model=OpenAIChat(
            id="gpt-4o",
            temperature=1,
            timeout=30
        ),
        name="Agent Team",
        team=agent_instances,
        add_history_to_messages=True,
        num_history_responses=3,
        show_tool_calls=False,
    )

    # 调用 agent team 执行任务
    response = agent_team.run(f"{prompt.message}", stream=False)

    # 获取 assistant 的最后一条消息
    assistant_content = None
    for message in response.messages:
        if message.role == "assistant" and message.content:
            assistant_content = message.content

    return {"result": True, "message": assistant_content}
