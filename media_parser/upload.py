import firebase_admin
from firebase_admin import credentials, firestore
from media_parser.telex import parse_telex, TelexRssEntry
import logging

logger = logging.getLogger()

# Application Default credentials are automatically created.
def dummy():
    cred = credentials.Certificate("mediaparser-2fc06-firebase-adminsdk-7jj0a-8ca91f0f24.json")
    app = firebase_admin.initialize_app(cred)
    db = firestore.client()

    telex_articles: list[TelexRssEntry] = parse_telex()

    db_ref = db.collection("telex_articles")
    for art in telex_articles:
        doc_ref = db_ref.document(art.guid)
        if not doc_ref.get().exists:
            logger.warning("%s -> New entry", art.guid)
            doc_ref.set(art.__dict__)