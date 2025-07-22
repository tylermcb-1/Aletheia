import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from fastmcp import FastMCP

slack_token = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=slack_token)
mcp = FastMCP("Slack MCP")

def summarize_thread(messages):
    if not messages:
        return "No messages in thread."
    if len(messages) == 1:
        return messages[0].get("text", "")
    return f"{messages[0].get('text', '')}\n↳ {messages[1].get('text', '')}"

def format_results(results):
    formatted = []
    for item in results:
        formatted.append({
            "permalink": item["permalink"],
            "summary": summarize_thread(item["thread"])
        })
    return formatted

@mcp.tool(name="slack.search_channel")
def search_channel(keyword: str, channel_name: str):
    try:
        channels = client.conversations_list(types="public_channel")["channels"]
        channel_id = next(c["id"] for c in channels if c["name"] == channel_name)

        messages = client.conversations_history(channel=channel_id, limit=100)["messages"]
        matches = [m for m in messages if keyword.lower() in m.get("text", "").lower()]

        results = []
        for m in matches:
            link = client.chat_getPermalink(channel=channel_id, message_ts=m["ts"])["permalink"]
            thread = client.conversations_replies(channel=channel_id, ts=m["ts"])["messages"]
            results.append({"permalink": link, "thread": thread})

        return format_results(results)

    except SlackApiError as e:
        return {"error": str(e)}

@mcp.tool(name="slack.search_group")
def search_group(keyword: str, group_name: str):
    try:
        groups = client.conversations_list(types="private_channel")["channels"]
        group_id = next(c["id"] for c in groups if c["name"] == group_name)

        messages = client.conversations_history(channel=group_id, limit=100)["messages"]
        matches = [m for m in messages if keyword.lower() in m.get("text", "").lower()]

        results = []
        for m in matches:
            link = client.chat_getPermalink(channel=group_id, message_ts=m["ts"])["permalink"]
            thread = client.conversations_replies(channel=group_id, ts=m["ts"])["messages"]
            results.append({"permalink": link, "thread": thread})

        return format_results(results)

    except SlackApiError as e:
        return {"error": str(e)}

@mcp.tool(name="slack.search_dm")
def search_dm(keyword: str, username: str):
    try:
        users = client.users_list()["members"]
        user_id = next(u["id"] for u in users if u["name"] == username or u["real_name"] == username)

        ims = client.conversations_list(types="im")["channels"]
        im_id = next(c["id"] for c in ims if c["user"] == user_id)

        messages = client.conversations_history(channel=im_id, limit=100)["messages"]
        matches = [m for m in messages if keyword.lower() in m.get("text", "").lower()]

        results = []
        for m in matches:
            link = client.chat_getPermalink(channel=im_id, message_ts=m["ts"])["permalink"]
            thread = client.conversations_replies(channel=im_id, ts=m["ts"])["messages"]
            results.append({"permalink": link, "thread": thread})

        return format_results(results)

    except SlackApiError as e:
        return {"error": str(e)}

@mcp.tool(name="slack.search_all_accessible")
def search_all_accessible(keyword: str, max_per_channel: int = 50, limit: int = 5):
    try:
        types = "public_channel,private_channel,im"
        conversations = client.conversations_list(types=types, limit=1000)["channels"]

        matched_results = []

        for conv in conversations:
            cid = conv["id"]
            cname = conv.get("name", f"(DM with {conv.get('user', 'unknown')})")
            try:
                messages = client.conversations_history(channel=cid, limit=max_per_channel)["messages"]
                matches = [m for m in messages if keyword.lower() in m.get("text", "").lower()]
                for m in matches:
                    link = client.chat_getPermalink(channel=cid, message_ts=m["ts"])["permalink"]
                    thread = client.conversations_replies(channel=cid, ts=m["ts"])["messages"]
                    matched_results.append({
                        "channel": cname,
                        "permalink": link,
                        "summary": summarize_thread(thread)
                    })
                    if len(matched_results) >= limit:
                        return matched_results
            except SlackApiError as e:
                continue  # skip inaccessible or archived channels
        return matched_results
    except SlackApiError as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()