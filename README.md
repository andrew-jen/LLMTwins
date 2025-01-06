# LLMTwins
https://docs.phidata.com/agents/introduction

## Environment

#### Environment Variables:
- OPENAI_API_KEY: OpenAI API Key

## Installation
```bash=
python3.10 -m venv env
source env/bin/active
pip3 install -r requirements.txt
```

## Run
```bash=
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

新增google_search功能來查找新聞
並透過postman可以於prompt網頁以post方法帶入json(role & message)，進而與ai互動
