from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import github_reviewer

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PRData(BaseModel):
    name : str
    id : int
    code : str

llm = ChatGroq(
    api_key=os.getenv("PRapi"),
    model="llama-3.3-70b-versatile"
)

prompt = ChatPromptTemplate.from_template(
    "You are expert in code review and you are given a pull request with the following code changes. Please review it and give feedback on bugs, readability and improvements : \n\n{code}"
)

chain = prompt | llm

@app.get("/home")
def home():
    return {"message": "Welcome to the PR review API!"}

@app.post("/reviewPR")
def review_PR(request: PRData):
    response = chain.invoke({"code" : request.code})
    return {"feedback": response.content}

@app.post("/webhook")
async def webhook(payload: dict):
    if payload["action"] == "opened":
        pr_number = payload["number"]
        repo = payload["repository"]["full_name"]
        
        diff = github_reviewer.fetch_pr_diff(repo, pr_number)
        comment = github_reviewer.review_code(diff, chain)
        github_reviewer.post_comment(repo, pr_number, comment)
        
    return {"status": "ok"}
    
