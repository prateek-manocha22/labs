from github_tool import get_pr_info
from claude_brain import summarize_pr

pr_data = get_pr_info("prateek-manocha22/demo-app", 1)
print("Step 1 done — PR read from GitHub")
print("Title:", pr_data["title"])
print()

result = summarize_pr(pr_data)
print("Step 2 done — Groq summarized the PR")
print()
print("SUMMARY:", result["summary"])
print("JIRA TITLE:", result["jira_title"])
print("RISKS:", result["risks"])
print("SLACK:", result["slack_message"])