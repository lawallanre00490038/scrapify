import json
import httpx
from urllib.parse import quote
from parse import parse_post
import requests, os

def scrape_user_posts(user_id: str, session: httpx.Client, page_size=12, max_pages: int = None):
    base_url = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
    variables = {
        "id": user_id,
        "first": page_size,
        "after": None,
    }
    _page_number = 1
    while True:
        resp = session.get(base_url + quote(json.dumps(variables)))
        data = resp.json()
        posts = data["data"]["user"]["edge_owner_to_timeline_media"]
        for post in posts["edges"]:
            yield parse_post(post["node"])  # note: we're using parse_post function from previous chapter
        page_info = posts["page_info"]
        if _page_number == 1:
            print(f"scraping total {posts['count']} posts of {user_id}")
        else:
            print(f"scraping page {_page_number}")
        if not page_info["has_next_page"]:
            break
        if variables["after"] == page_info["end_cursor"]:
            break
        variables["after"] = page_info["end_cursor"]
        _page_number += 1     
        if max_pages and _page_number > max_pages:
            break


# Example run:
if __name__ == "__main__":
    with httpx.Client(timeout=httpx.Timeout(20.0)) as session:
        posts = list(scrape_user_posts("1067259270", session, max_pages=3))
        data = json.dumps(posts, indent=2, ensure_ascii=False)
        # print(data)


  
# # Function to download media
# def download_file(url, folder, filename):
#     response = requests.get(url, stream=True)
#     if response.status_code == 200:
#         file_path = os.path.join(folder, filename)
#         with open(file_path, 'wb') as f:
#             for chunk in response.iter_content(1024):
#                 f.write(chunk)
#         print(f"Downloaded {filename}")
#     else:
#         print(f"Failed to download {filename}")

# # Process each item in the data
# for idx, item in enumerate(data):
#     # Download video
#     if "video_url" in item and item["video_url"]:
#         video_url = item["video_url"]
#         video_filename = f"video_{idx + 1}.mp4"
#         download_file(video_url, "videos", video_filename)

#     # Download image
#     if "src" in item and item["src"]:
#         image_url = item["src"]
#         image_filename = f"image_{idx + 1}.jpg"
#         download_file(image_url, "images", image_filename)

#     # Save captions
#     if "captions" in item and item["captions"]:
#         caption_text = item["captions"][0]
#         caption_filename = f"caption_{idx + 1}.txt"
#         with open(os.path.join("captions", caption_filename), 'w', encoding='utf-8') as f:
#             f.write(caption_text)
#         print(f"Saved caption_{idx + 1}.txt")

# print("Download process complete.")

# Directory to save videos
save_directory = "./downloaded_videos/"


# Download each video
for post in data:
    if post.get("is_video") and post.get("video_url"):
        video_url = post["video_url"]
        video_id = post.get("id", "unknown")
        video_filename = f"{save_directory}{video_id}.mp4"
        
        print(f"Downloading video from {video_url}...")
        
        response = requests.get(video_url)
        if response.status_code == 200:
            with open(video_filename, "wb") as video_file:
                video_file.write(response.content)
            print(f"Video saved as {video_filename}")
        else:
            print(f"Failed to download video from {video_url}")