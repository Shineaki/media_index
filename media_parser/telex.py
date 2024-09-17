from rss_parser import RSSParser
from rss_parser.models.rss.item import Item
import requests
from datetime import datetime

class TelexRssEntry:
    def __init__(self, entry: Item) -> None:
        self.title: str = entry.title.content
        self.link: str = entry.link.content
        self.guid: str = entry.guid.content.split("/")[-1]
        self.pub_date: str = datetime.strptime(entry.pub_date.content, "%a, %d %b %Y %H:%M:%S %z")
        self.category: str = entry.category.content
        self.description: str = entry.description.content
        self.image: str = entry.enclosure.attributes.get("url", "") if entry.enclosure else ""
    
def parse_telex():
    rsp = requests.get("https://telex.hu/rss")
    rss = RSSParser.parse(rsp.text)

    relevant_categories = ["Belföld", "Külföld", "Gazdaság"]

    posts = []

    for item in rss.channel.items:
        if item.category.content in relevant_categories:
            posts.append(TelexRssEntry(item))
    return posts
