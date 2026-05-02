# ============================================================================
# GitHub Reviewer Module
# Handles all GitHub API interactions for fetching PRs and posting reviews
# ============================================================================

import requests  # HTTP library for making API calls
import os  # For accessing environment variables

def fetch_pr_diff(repo, pr_number):
    """Fetch the code diff/patch for a specific pull request from GitHub
    
    Args:
        repo: Repository name in format 'owner/repo' (e.g., '28harivijay/ai-pr-review-bot')
        pr_number: The pull request number to fetch
    
    Returns:
        String containing the concatenated diff/patch of all changed files in the PR
    """
    # Construct GitHub API URL to get all files changed in the PR
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    
    # Make authenticated request to GitHub API
    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {os.getenv('PRgit')}",  # GitHub API token
            "Accept": "application/vnd.github.v3+json"  # API version
        }
    )
    
    # Parse the JSON response containing file information
    files = response.json()
    
    # Concatenate all file patches into a single diff string
    diff = ""
    for file in files:
        # Each file has a 'patch' field containing the diff
        diff += file.get("patch", "")
    
    return diff


def review_code(diff, chain):
    """Generate an AI-powered code review for the given PR diff
    
    Args:
        diff: String containing the code diff/patch to review
        chain: LangChain prompt-LLM chain that performs the review
    
    Returns:
        String containing the AI-generated review feedback
    """
    # Invoke the LLM chain with the diff to get review feedback
    response = chain.invoke({"code": diff})
    return response.content

def post_comment(repo, pr_number, comment):
    """Post the AI-generated review as a comment on the GitHub pull request
    
    Args:
        repo: Repository name in format 'owner/repo'
        pr_number: The pull request number to comment on
        comment: The review text to post as a comment
    
    Returns:
        None (posts comment directly via GitHub API)
    """
    # Construct GitHub API URL to post comments on the PR
    # Note: GitHub treats PRs as issues in their API, hence '/issues/' endpoint
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    
    # Make authenticated POST request to GitHub API
    requests.post(
        url,
        headers={
            "Authorization": f"Bearer {os.getenv('PRgit')}",  # GitHub API token
            "Accept": "application/vnd.github.v3+json"  # API version
        },
        json={"body": comment}  # Comment text to post
    )
