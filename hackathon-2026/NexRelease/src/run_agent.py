from github_tool import get_pr_info
from claude_brain import summarize_pr
from jira_tool import create_jira_ticket
from slack_tool import post_slack_message
from calendar_tool import create_calendar_event

def run_agent(repo, pr_number):
    print("\n" + "="*50)
    print("RELEASE AGENT STARTED")
    print("="*50 + "\n")

    # Step 1: Read PR from GitHub
    print("Step 1: Reading PR from GitHub...")
    pr_data = get_pr_info(repo, pr_number)
    print(f"  Title: {pr_data['title']}")
    print(f"  Author: {pr_data['author']}")
    print(f"  CI Status: {pr_data['ci_status']}")
    print()

    # Step 2: Summarize with Groq
    print("Step 2: Summarizing PR with Groq...")
    summary = summarize_pr(pr_data)
    print(f"  Summary: {summary['summary'][:80]}...")
    print()

    # Step 3: Create Jira ticket
    print("Step 3: Creating Jira ticket...")
    ticket = create_jira_ticket(
        title=summary["jira_title"],
        description=summary["summary"],
        checklist=summary["checklist"],
        risks=summary["risks"]
    )
    print(f"  Ticket: {ticket.get('url', 'failed')}")
    print()

    # Step 4: Post to Slack
    print("Step 4: Posting to Slack...")
    slack_message = f"""
*New Release* — `{pr_data['title']}`
*Author:* {pr_data['author']}
*CI Status:* {pr_data['ci_status']}

{summary['slack_message']}

*Jira Ticket:* {ticket.get('url', 'N/A')}
*PR Link:* {pr_data['pr_url']}
    """.strip()
    
    slack_result = post_slack_message(slack_message)
    print(f"  Slack: {'posted' if slack_result['success'] else 'failed'}")
    print()

    # Step 5: Schedule meeting
    print("Step 5: Scheduling go/no-go meeting...")
    # NEW
    meeting = create_calendar_event(
    meeting_title=summary["meeting_title"],
    pr_url=pr_data["pr_url"],
    risks=summary["risks"]
    )
    print()

    print("="*50)
    print("AGENT COMPLETE")
    print("="*50)

    return {
        "pr_title": pr_data["title"],
        "summary": summary["summary"],
        "jira_url": ticket.get("url", ""),
        "slack_posted": slack_result["success"],
        "meeting": meeting["time"]
    }


# Run it
if __name__ == "__main__":
    result = run_agent("prateek-manocha22/demo-app", 1)
    print("\nFinal result:", result)