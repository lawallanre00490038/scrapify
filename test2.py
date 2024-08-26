from scrapfly import ScrapflyClient, ScrapeConfig

# SCRAPFLY = ScrapflyClient("YOUR SCRAPFLY KEY")

# async def scrape_user_posts(user_id: str, page_size=50, max_pages: Optional[int] = None):
#     """Scrape all posts of an instagram user of given numeric user id"""
#     base_url = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
#     variables = {
#         "id": user_id,
#         "first": page_size,
#         "after": None,
#     }
#     _page_number = 1
#     while True:
#         url = base_url + quote(json.dumps(variables))
#         result = await SCRAPFLY.async_scrape(ScrapeConfig(url, **BASE_CONFIG))
#         data = json.loads(result.content)
#         posts = data["data"]["user"]["edge_owner_to_timeline_media"]
#         for post in posts["edges"]:
#             yield parse_post(post["node"])
#         page_info = posts["page_info"]
#         if _page_number == 1:
#             print(f"scraping total {posts['count']} posts of {user_id}")
#         else:
#             print(f"scraping posts page {_page_number}")
#         if not page_info["has_next_page"]:
#             break
#         if variables["after"] == page_info["end_cursor"]:
#             break
#         variables["after"] = page_info["end_cursor"]
#         _page_number += 1
#         if max_pages and _page_number > max_pages:
#             break


# standard web scraping code
import httpx
from parsel import Selector

response = httpx.get("some instagram.com URL")
selector = Selector(response.text)

# in ScrapFly becomes this 👇
from scrapfly import ScrapeConfig, ScrapflyClient

# replaces your HTTP client (httpx in this case)
scrapfly = ScrapflyClient(key="Your ScrapFly API key")

response = scrapfly.scrape(ScrapeConfig(
    url="website URL",
    asp=True, # enable the anti scraping protection to bypass blocking
    country="US", # set the proxy location to a specfic country
    render_js=True # enable rendering JavaScript (like headless browsers) to scrape dynamic content if needed
))

# use the built in Parsel selector
selector = response.selector
# access the HTML content
html = response.scrape_result['content']