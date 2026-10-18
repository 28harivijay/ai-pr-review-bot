# AI PR Review Bot

An AI-powered GitHub pull request reviewer built with **FastAPI**, **LangChain**, and **Groq**. It can review pull request diffs manually through an API endpoint or automatically when GitHub sends pull request webhook events.

## Features

- Reviews pull request diffs using an AI language model.
- Supports manual reviews through the `/reviewPR` endpoint.
- Automatically reviews pull requests when they are opened, reopened, or updated.
- Fetches changed-file patches from the GitHub API.
- Posts generated review feedback as a comment on the pull request.
- Limits very large diffs to keep requests manageable.

## Project structure

```text
.
├── backend/
│   ├── github_reviewer.py  # GitHub API and review helper functions
│   ├── main.py             # FastAPI application and API routes
│   └── .gitignore
└── test.txt
```

## Requirements

- Python 3.10+
- A Groq API key
- A GitHub personal access token with permission to read pull requests and create issue comments
- A public URL for the webhook endpoint when using automatic reviews

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/28harivijay/ai-pr-review-bot.git
   cd ai-pr-review-bot/backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   On Windows PowerShell:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:

   ```bash
   pip install fastapi uvicorn python-dotenv requests langchain-core langchain-groq
   ```

4. Create a `.env` file in the `backend` directory:

   ```env
   PRapi=your_groq_api_key
   PRgit=your_github_token
   ```

   Keep this file private. It is ignored by Git through `backend/.gitignore`.

## Running the API

From the `backend` directory, start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API endpoints

### Health check

```http
GET /home
```

Example response:

```json
{
  "message": "Welcome to the PR review API!"
}
```

### Manual pull request review

```http
POST /reviewPR
Content-Type: application/json
```

Request body:

```json
{
  "name": "Example PR",
  "id": 123,
  "code": "diff --git a/example.py b/example.py\n+print('Hello')"
}
```

Example response:

```json
{
  "feedback": "...AI-generated review feedback..."
}
```

> Note: The current endpoint accepts `name` and `id` for request compatibility, but the review is generated from the `code` field.

### GitHub webhook

```http
POST /webhook
```

Configure a GitHub repository webhook to send pull request events to this endpoint. The bot processes these actions:

- `opened`
- `reopened`
- `synchronize`

When one of these events is received, the bot fetches the pull request diff, sends it to the AI model, and posts the generated feedback as a pull request comment.

## GitHub webhook setup

1. Deploy the FastAPI application to a server with a publicly accessible HTTPS URL.
2. Open your GitHub repository's **Settings → Webhooks** page.
3. Add a webhook pointing to:

   ```text
   https://your-domain.example/webhook
   ```

4. Set the content type to `application/json`.
5. Select ** individual events ** and enable **Pull requests**, or use the events appropriate for your deployment.
6. Save the webhook and open or update a pull request to test it.

## Review format

The AI reviewer is instructed to organize useful feedback under these headings when applicable:

- Bugs
- Security
- Readability
- Suggestions

Each issue should identify the affected file and explain the problem concisely, with a short fix example when useful.

## Security notes

- Never commit `.env` files, API keys, or GitHub tokens.
- Use a GitHub token with the minimum permissions required by your deployment.
- Restrict CORS origins before deploying to production. The current application allows requests from all origins for development convenience.
- Add webhook signature verification before exposing the endpoint publicly in a production environment.
- Consider adding authentication and rate limiting to the API.

## How it works

1. GitHub sends a pull request webhook event to `/webhook`.
2. The application extracts the repository name and pull request number.
3. `github_reviewer.py` fetches the changed-file patches through the GitHub API.
4. The diff is sent to the LangChain/Groq model chain.
5. The generated review is posted as a comment on the pull request.

## License

No license has been declared for this repository yet. Add a license if you plan to distribute or accept external contributions.
