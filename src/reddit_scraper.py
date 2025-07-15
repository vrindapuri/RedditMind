import os
import praw
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debug log
print("[DEBUG] Reddit client ID:", os.getenv("REDDIT_CLIENT_ID"))

def get_reddit_client():
    """Initialize the Reddit client using credentials from the .env file."""
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        raise ValueError("[ERROR] Missing Reddit API credentials in .env")

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

def extract_username_from_url(url_or_name: str) -> str:
    """
    Extract the username from a Reddit profile URL, or return the username if already provided.
    Examples:
    - 'https://www.reddit.com/user/spez' -> 'spez'
    - 'spez' -> 'spez'
    """
    if "reddit.com/user/" in url_or_name:
        return url_or_name.rstrip("/").split("/")[-1]
    return url_or_name.strip()

def scrape_user_data(url_or_username, post_limit=20, comment_limit=20):
    """
    Scrapes a user's recent posts and comments from Reddit using PRAW.
    Also attempts to fetch the user's profile image URL (`icon_img`).
    """
    reddit = get_reddit_client()
    username = extract_username_from_url(url_or_username)

    posts = []
    comments = []
    profile_image = None

    try:
        user = reddit.redditor(username)

        # Fetch profile image
        profile_image = getattr(user, "icon_img", None)

        # Fetch recent posts
        for post in user.submissions.new(limit=post_limit):
            posts.append({
                "title": post.title,
                "body": post.selftext,
                "url": f"https://www.reddit.com{post.permalink}"
            })

        # Fetch recent comments
        for comment in user.comments.new(limit=comment_limit):
            comments.append({
                "body": comment.body,
                "url": f"https://www.reddit.com{comment.permalink}"
            })

    except Exception as e:
        print(f"[ERROR] Couldn't fetch data for {username}: {e}")
        return {
            "icon_img": None,
            "posts": [],
            "comments": []
        }

    return {
        "icon_img": profile_image,
        "posts": posts,
        "comments": comments
    }
