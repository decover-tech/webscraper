import hashlib
import re

from bs4 import BeautifulSoup
import os
import requests
from urllib.parse import urlparse

download_dir = ""


def get_text_from_html(html_content):
    soup = BeautifulSoup(html_content, features="html.parser")

    # kill all script and style elements.
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = ' '.join(chunk for chunk in chunks if chunk)
    return text


def get_pdf_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find all <a> tags that have an 'href' attribute ending with '.pdf'
    pdf_links = soup.find_all('a', href=lambda x: x and x.endswith('.pdf'))
    return pdf_links


def download_pdf(pdf_link):
    downloaded_pdfs = []
    pdf_path = os.path.join(download_dir, os.path.basename(pdf_link))

    with requests.get(pdf_link, stream=True) as response:
        if response.status_code == 200:
            with open(pdf_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            downloaded_pdfs.append(pdf_path)

    return downloaded_pdfs


def normalize_string(input_string: str) -> str:
    # Remove punctuation
    normalized_string = re.sub(r'[^\w\s-]', '', input_string)
    # Convert to lowercase
    normalized_string = normalized_string.lower()
    # Capitalize the first letter of each word
    normalized_string = normalized_string.title()
    # Remove multiple spaces
    normalized_string = re.sub(r'\s+', ' ', normalized_string).strip()
    # Retain hyphens between consecutive words
    return re.sub(r'(\b\w)-(\w\b)', r'\1\2', normalized_string)


# Take the last part of the URL and guess the closest file name.
# Keep it normalized, subject to the following rules:
# 1. Remove punctuation
# 2. Convert to lowercase
# 3. Capitalize the first letter of each word
# 4. Remove multiple spaces
# 5. Retain hyphens between consecutive words
def extract_file_name_from_url(url: str) -> str:
    # Remove the protocol and domain name from the URL.
    url = url.replace('https://', '').replace('http://', '')
    # Remove the trailing slash.
    url = url.rstrip('/')
    # Split the URL by slashes.
    url_parts = url.split('/')
    # Take the last part of the URL.
    file_name = url_parts[-1]
    # Take MD5 hash of the URL
    return hashlib.md5(file_name.encode()).hexdigest() + '.txt'


def extract_domain(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:
        return parsed_url.netloc
    elif parsed_url.netloc:
        return parsed_url.netloc
    else:
        return parsed_url.path.split('/')[0]
