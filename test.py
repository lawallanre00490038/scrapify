import json
import httpx
from urllib.parse import quote
import os
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from parse import parse_post

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
            yield parse_post(post["node"])  # Using parse_post function
        page_info = posts["page_info"]
        if _page_number == 1:
            print(f"Scraping total {posts['count']} posts of {user_id}")
        else:
            print(f"Scraping page {_page_number}")
        if not page_info["has_next_page"]:
            break
        if variables["after"] == page_info["end_cursor"]:
            break
        variables["after"] = page_info["end_cursor"]
        _page_number += 1     
        if max_pages and _page_number > max_pages:
            break

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def download_file(url, folder, filename):
    file_path = os.path.join(folder, filename)
    if os.path.exists(file_path):
        print(f"Skipping {filename}, I have already been downloaded.")
        return  # Skip if the file already exists
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise HTTPError for bad responses
    if response.status_code == 200:
        os.makedirs(folder, exist_ok=True)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename}")

if __name__ == "__main__":
    with httpx.Client(timeout=httpx.Timeout(20.0)) as session:
        user_id = "202315962" # Instagram user id
        posts = list(scrape_user_posts(user_id, session, max_pages=40))
        data = json.dumps(posts, indent=2, ensure_ascii=False)

    # Save posts to a JSON file (optional)
    with open("posts.json", "w", encoding="utf-8") as f:
        f.write(data)
    
    # Directory to save media
    video_directory = "./downloaded_videos/"
    image_directory = "./downloaded_images/"
    caption_directory = "./downloaded_captions/"

    # Process each post and download media
    for idx, post in enumerate(posts):
        if post.get("is_video") and post.get("video_url"):
            video_url = post["video_url"]
            video_filename = f"video_{idx + 1}.mp4"
            download_file(video_url, video_directory, video_filename)

        if post.get("src"):
            image_url = post["src"]
            image_filename = f"image_{idx + 1}.jpg"
            download_file(image_url, image_directory, image_filename)

        if post.get("captions"):
            caption_text = post["captions"][0]
            caption_filename = f"caption_{idx + 1}.txt"
            caption_path = os.path.join(caption_directory, caption_filename)
            os.makedirs(caption_directory, exist_ok=True)
            if not os.path.exists(caption_path):
                with open(caption_path, 'w', encoding='utf-8') as f:
                    f.write(caption_text)
                print(f"Saved {caption_filename}")
            else:
                print(f"Skipping {caption_filename}, already saved.")

    print("Download process complete.")
