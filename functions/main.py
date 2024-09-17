# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import scheduler_fn
from firebase_admin import initialize_app
from rss_parser import RSSParser
from rss_parser.models.rss.item import Item
from firebase_admin import firestore
import requests
from datetime import datetime

import logging

logger = logging.getLogger()

initialize_app()

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

@scheduler_fn.on_schedule(schedule="0 * * * *", region="europe-west1")
def hourly_telex_parsing(event: scheduler_fn.ScheduledEvent) -> None:
    db = firestore.client()
    telex_articles: list[TelexRssEntry] = parse_telex()
    db_ref = db.collection("telex_articles")
    for art in telex_articles:
        doc_ref = db_ref.document(art.guid)
        if not doc_ref.get().exists:
            logger.warning("%s -> New entry", art.guid)
            doc_ref.set(art.__dict__)