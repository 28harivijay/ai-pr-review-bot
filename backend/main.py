# ============================================================================
# PR Review Bot - Main Application
# This FastAPI app provides endpoints for automated code review using AI
# ============================================================================

from dotenv import load_dotenv  # Load environment variables from .env file
import os
from langchain_groq import ChatGroq  # Groq LLM integration
from langchain_core.prompts import ChatPromptTemplate  # For creating prompt templates
from fastapi import FastAPI  # Web framework for building APIs
from pydantic import BaseModel  # Data validation using type hints
from typing import List
from fastapi.middleware.cors import CORSMiddleware  # Handle CORS requests
import github_reviewer  # Custom module for GitHub interactions

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application
app = FastAPI()

# Configure CORS (Cross-Origin Resource Sharing) to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Request model for PR review endpoint
class PRData(BaseModel):
    """Data model for pull request review requests"""
    name: str  # Name of the PR or project
    id: int  # PR ID or identifier
    code: str  # Code snippet to be reviewed

# Initialize the Language Model (LLM) using Groq's API
# Groq provides fast inference for LLaMA models
llm = ChatGroq(
    api_key=os.getenv("PRapi"),  # API key from environment variables
    model="llama-3.3-70b-versatile"  # Using LLaMA 3.3 70B model
)

# Define the prompt template for code review
# This template instructs the AI to act as an expert code reviewer
prompt = ChatPromptTemplate.from_template(
    "You are expert in code review and you are given a pull request with the following code changes. Please review it and give feedback on bugs, readability and improvements : \n\n{code}"
)

# Create a chain that connects the prompt template to the LLM
# The pipe operator (|) chains the prompt template output as input to the LLM
chain = prompt | llm

# Health check endpoint
@app.get("/home")
def home():
    """Health check endpoint to verify API is running"""
    return {"message": "Welcome to the PR review API!"}

# Manual PR review endpoint
@app.post("/reviewPR")
def review_PR(request: PRData):
    """Accepts PR data and returns AI-generated code review feedback
    
    Args:
        request: PRData object containing name, id, and code to review
    
    Returns:
        Dictionary with 'feedback' key containing the AI review
    """
    # Send the code to the LLM chain for review
    response = chain.invoke({"code": request.code})
    return {"feedback": response.content}

# GitHub webhook endpoint for automatic PR reviews
@app.post("/webhook")   
async def webhook(payload: dict):
    """Receives GitHub webhook events and automatically reviews new PRs
    
    Listens for PR 'opened' events, fetches the diff, generates a review, 
    and posts it as a comment on the PR.
    
    Args:
        payload: GitHub webhook payload containing PR information
    
    Returns:
        Status confirmation
    """
    # Check if the webhook event is a PR being opened
    if payload["action"] == "opened":
        pr_number = payload["number"]
        repo = payload["repository"]["full_name"]
        
        # Fetch the PR diff from GitHub
        diff = github_reviewer.fetch_pr_diff(repo, pr_number)
        
        # Generate code review using the LLM chain
        comment = github_reviewer.review_code(diff, chain)
        
        # Post the review as a comment on the PR
        github_reviewer.post_comment(repo, pr_number, comment)
        
    return {"status": "ok"}
    
