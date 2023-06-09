# Create a python object with getters and setters with the following properties
# Use strong types
# Class Name: Parsed Object

# File URL: Path to S3 bucket where the is stored
# Jurisdiction: The jurisdiction where the law is applicable
# Source URL: The URL of the webpage from where it was downloaded
# Category: LAW, ACT, STATURE, JURISDICTION, etc.
# SubCategory: DIVORCE, TAX, CRIMINAL, etc.
# Date: When was the last time the object was indexed.
# Hash: MD5 hash of the contents to detect any changes
# Title: Title associated with the file contents

from typing import Optional
from datetime import datetime

class ParsedObject:
    """
    Represents the final parsed object that is generated by Crawlumbus.
    """
    def __init__(self, file_url: Optional[str] = None,
                 jurisdiction: Optional[str] = None,
                 source_url: Optional[str] = None,
                 category: Optional[str] = None,
                 subcategory: Optional[str] = None,
                 date: Optional[datetime] = None,
                 hash: Optional[str] = None,
                 title: Optional[str] = None):
        self._file_url = file_url
        self._jurisdiction = jurisdiction
        self._source_url = source_url
        self._category = category
        self._subcategory = subcategory
        self._date = date
        self._hash = hash
        self._title = title

    @property
    def file_url(self):
        return self._file_url

    @file_url.setter
    def file_url(self, value: str):
        self._file_url = value

    @property
    def jurisdiction(self):
        return self._jurisdiction

    @jurisdiction.setter
    def jurisdiction(self, value: str):
        self._jurisdiction = value

    @property
    def source_url(self):
        return self._source_url

    @source_url.setter
    def source_url(self, value: str):
        self._source_url = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value: str):
        self._category = value

    @property
    def subcategory(self):
        return self._subcategory

    @subcategory.setter
    def subcategory(self, value: str):
        self._subcategory = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value: datetime):
        self._date = value

    @property
    def hash(self):
        return self._hash

    @hash.setter
    def hash(self, value: str):
        self._hash = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    def __str__(self):
        return f'ParsedObject({self._file_url}, {self._jurisdiction}, {self._source_url}, {self._category}, ' \
               f'{self._subcategory}, {self._date}, {self._hash}, {self._title})'

    def __dict__(self):
        return {
            'file_url': self._file_url,
            'jurisdiction': self._jurisdiction,
            'source_url': self._source_url,
            'category': self._category,
            'subcategory': self._subcategory,
            'date': self._date,
            'hash': self._hash,
            'title': self._title,
        }