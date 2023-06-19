from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime, func

db = SQLAlchemy()


class CrawlerRun(db.Model):
    __tablename__ = 'crawler_run'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    run_number = Column(Integer)
    num_pages_crawled = Column(Integer)
    num_laws_crawled = Column(Integer)
    num_websites_crawled = Column(Integer)

    def __init__(self, run_number, num_pages_crawled, num_laws_crawled, num_websites_crawled):
        self.run_number = run_number
        self.num_pages_crawled = num_pages_crawled
        self.num_laws_crawled = num_laws_crawled
        self.num_websites_crawled = num_websites_crawled