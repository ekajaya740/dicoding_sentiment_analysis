import os
import csv
import time
from googleapiclient.discovery import build
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
VIDEO_ID = os.getenv("VIDEO_ID")
MAX_RESULTS = 100
REQUEST_DELAY = 0.1


def setup_youtube_client():
    return build("youtube", "v3", developerKey=API_KEY)


def get_video_info(client, video_id):
    try:
        request = client.videos().list(part="snippet,statistics", id=video_id)
        response = request.execute()

        if response["items"]:
            video = response["items"][0]
            stats = video["statistics"]
            return {
                "title": video["snippet"]["title"],
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
            }
    except Exception as e:
        print(f"Error fetching video info: {e}")
    return None


def get_all_comments(client, video_id):
    all_comments = []
    next_page_token = None

    while True:
        try:
            request = client.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=MAX_RESULTS,
                pageToken=next_page_token,
                textFormat="plainText",
            )
            response = request.execute()

            for item in response["items"]:

                main_comment = item["snippet"]["topLevelComment"]["snippet"]
                comment_data = {
                    "id": item["snippet"]["topLevelComment"]["id"],
                    "author": main_comment["authorDisplayName"],
                    "date": main_comment["publishedAt"],
                    "text": main_comment["textDisplay"],
                    "likes": main_comment["likeCount"],
                    "reply_count": item["snippet"]["totalReplyCount"],
                    "is_reply": False,
                }
                all_comments.append(comment_data)

                if "replies" in item:
                    for reply in item["replies"]["comments"]:
                        reply_snippet = reply["snippet"]
                        reply_data = {
                            "id": reply["id"],
                            "author": reply_snippet["authorDisplayName"],
                            "date": reply_snippet["publishedAt"],
                            "text": reply_snippet["textDisplay"],
                            "likes": reply_snippet["likeCount"],
                            "reply_count": 0,
                            "is_reply": True,
                        }
                        all_comments.append(reply_data)

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            print(f"Error fetching comments: {e}")
            break

    return all_comments


def save_comments_to_csv(comments, filename, folder="dataset"):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "author",
                "date",
                "text",
                "likes",
                "reply_count",
                "is_reply",
            ],
        )
        writer.writeheader()
        writer.writerows(comments)

    print(f"Saved {len(comments)} comments to {file_path}")
    return file_path


def main():
    print("Scraping Video Comments...")
    youtube = setup_youtube_client()
    get_video_info(youtube, VIDEO_ID)
    comments = get_all_comments(youtube, VIDEO_ID)

    if not comments:
        print("No comments found!")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"youtube_comments_{timestamp}.csv"
    save_comments_to_csv(comments, filename)

    print(f"Saved {len(comments)} comments to {filename}")


if __name__ == "__main__":
    main()
