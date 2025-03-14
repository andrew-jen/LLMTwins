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

description:
將agents與主程式拆開，讓agents變成可以持續擴增和調整的檔案，同時加入JWT作為使用者身分驗證的金鑰，
在資料庫中儲存不同使用者的id、金鑰、以及對應可以調用的agent & tools，
這樣就能實現在同一個產品上依據用戶權限的不同，提供不同服務的功能。

operate:
透過postman可以於prompt網頁以post方法帶入json(role & message)以及金鑰，進而與ai互動
