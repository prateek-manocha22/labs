"""
MCP Agent Starter Kit
A minimal agent that uses a tool (search) via the MCP pattern.
"""
import json
import os

# ── Tool definitions (MCP "tools" spec) ───────────────────────────────────────
TOOLS = [
    {
        "name": "search_github_issues",
        "description": "Search for open issues in a GitHub repo by keyword.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo":    {"type": "string", "description": "Owner/repo e.g. toon-format/toon"},
                "keyword": {"type": "string", "description": "Filter keyword"},
            },
            "required": ["repo"],
        },
    }
]


def execute_tool(name: str, args: dict) -> str:
    """Dispatch tool calls to real implementations."""
    if name == "search_github_issues":
        return search_github_issues(**args)
    return f"Unknown tool: {name}"


def search_github_issues(repo: str, keyword: str = "") -> str:
    """Real GitHub API call — replace with MCP server in production."""
    import requests
    url = f"https://api.github.com/repos/{repo}/issues?state=open"
    try:
        data = requests.get(url, timeout=5).json()
        issues = [i for i in data if keyword.lower() in i.get("title", "").lower()]
        return json.dumps([{"id": i["number"], "title": i["title"]} for i in issues[:5]])
    except Exception as e:
        return f"Error: {e}"


def run_agent(user_query: str):
    """
    A simple agentic loop: send query + tools to LLM → execute any tool call → return final answer.
    Update this function with your real LLM provider (OpenAI / Anthropic / Gemini).
    """
    print(f"[Agent] Received: {user_query}")

    # ── Replace this block with a real LLM call ───────────────────────────────
    # Example with OpenAI:
    # from openai import OpenAI
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     tools=TOOLS,
    #     messages=[{"role": "user", "content": user_query}],
    # )
    # ─────────────────────────────────────────────────────────────────────────

    # Placeholder: simulate a tool call
    simulated_tool_call = {"name": "search_github_issues", "args": {"repo": "toon-format/toon"}}
    tool_result = execute_tool(simulated_tool_call["name"], simulated_tool_call["args"])

    print(f"[Tool Result] {tool_result}")
    return tool_result


if __name__ == "__main__":
    run_agent("Find open issues in the toon-format repo related to parsing")
