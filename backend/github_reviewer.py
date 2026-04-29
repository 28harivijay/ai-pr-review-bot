import requests
import os

def fetch_pr_diff(repo, pr_number):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {os.getenv('PRgit')}",
            "Accept": "application/vnd.github.v3+json"
        }
    )
    files = response.json()
    diff = ""
    for file in files:
        diff += file.get("patch", "")
    return diff


def review_code(diff,chain):
    response = chain.invoke({"code": diff})
    return response.content

def post_comment(repo, pr_number, comment):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    requests.post(
        url,
        headers={
            "Authorization": f"Bearer {os.getenv('PRgit')}",
            "Accept": "application/vnd.github.v3+json"
        },
        json={"body": comment}
    )
