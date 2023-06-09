# Fixes error "Alternative syntax for unions requires Python 3.10 or newer"
from __future__ import annotations

import logging
import os
import re
import tempfile
import urllib
from io import StringIO
from logging.config import dictConfig

import pytesseract
import requests
from PIL import Image
from pdf2image import convert_from_path
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from docx import Document
from typing import IO

from drivers.utilities.s3_client import S3Client

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


def read_pdf_with_ocr(file_path):
    """
    This method reads the contents of a PDF using OCR.
    :param file_path: The path to the PDF file.
    :return: The contents of the file.
    """
    logging.info(f"Reading PDF with OCR: {file_path}")
    # Step I: Convert PDF to JPG.
    pdf_pages = convert_from_path(file_path, 500)

    # Step II: Create tempdir if it does not exist
    tempdir = os.path.join(os.path.dirname(file_path), 'temp')
    if not os.path.exists(tempdir):
        os.mkdir(tempdir)

    # Step III: List of image files.
    image_file_list = []
    result = ''

    # Step IV: Convert PDF to JPG
    for page_enumeration, page in enumerate(pdf_pages, start=1):
        # Create a file name to store the image
        filename = f"{tempdir}/page_{page_enumeration:03}.jpg"

        # Declaring filename for each page of PDF as JPG
        # For each page, filename will be:
        # PDF page 1 -> page_001.jpg
        # PDF page 2 -> page_002.jpg
        # PDF page 3 -> page_003.jpg
        # PDF page n -> page_00n.jpg
        # ....

        # Save the image of the page in system
        page.save(filename, "JPEG")
        image_file_list.append(filename)
        text = str((pytesseract.image_to_string(Image.open(filename))))

        # Replace \n with space
        text = text.replace('-\n', '')
        result += text

        # Delete the temp file.
        if os.path.exists(filename):
            os.remove(filename)

    # Step V: Delete the temp directory.
    if os.path.exists(tempdir):
        os.rmdir(tempdir)

    # Step VI: Return the result
    return result


def read_local_file(file_path):
    """
    This method reads the contents of a file from the local file system.
    :param file_path:
    :return: The contents of the file.
    """
    # Raise an exception if the file does not exist.
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")

    logging.info(f"Reading local file: {file_path}")
    if file_path.endswith('.pdf'):  # Check if the input_file_name is a PDF
        with open(os.path.join(file_path), 'rb') as f:  # Open the PDF and extract its contents
            resource_manager = PDFResourceManager()
            string_io = StringIO()
            converter = TextConverter(resource_manager, string_io)
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            for page in PDFPage.get_pages(f):
                page_interpreter.process_page(page)
        file_contents = string_io.getvalue()
        converter.close()
        string_io.close()
        contents_normalized = re.sub('[^a-zA-Z0-9. ]+', '', file_contents)
        if len(contents_normalized) > 0:
            return contents_normalized
        else:
            file_contents = read_pdf_with_ocr(file_path)
        return file_contents

    # Check if the input_file_name is a docx
    if file_path.endswith('.docx'):
        doc = Document(file_path)
        fullText = []
        for paragraph in doc.paragraphs:
            fullText.append(paragraph.text)
        return '\n'.join(fullText)
    else:
        # If the input_file_name is not a PDF, it is assumed to be a regular text input_file_name
        # Open the input_file_name and read its contents
        with open(os.path.join(file_path), 'r') as f:
            file_contents = f.read()
    return file_contents


def read_local_file_with_ocr(file_path):
    """
    This method reads the contents of a file from the local file system using OCR.
    :param file_path:
    :return: The contents of the file.
    """
    with open(os.path.join(file_path), 'rb') as f:  # Open the PDF and extract its contents
        resource_manager = PDFResourceManager()
        string_io = StringIO()
        converter = TextConverter(resource_manager, string_io)
        page_interpreter = PDFPageInterpreter(resource_manager, converter)
        for page in PDFPage.get_pages(f):
            page_interpreter.process_page(page)
    contents = string_io.getvalue()
    converter.close()
    string_io.close()
    return contents


class File:
    """
    This class is responsible for reading the contents of a file.
    Supports the following:
    1. Reading a text file from a URL. (Done)
    2. Reading a PDF file using OCR. (Done)
    3. Reading a text file from S3. (Done)
    4. Reading a text file from the local file system. (DONE)
    5. Reading a docx file from the local file system. (DONE)
    """

    def __init__(self):
        # The S3 client is used to read files from S3.
        self.s3_client = S3Client()
        self.contents = ''

    def read(self, file_path: str) -> str:
        """
        This method reads the contents of a file and returns it.
        :param file_path: The path of the file.
        :return: The contents of the file.
        """
        # Step I: Check if the file is on S3.
        logging.info(f"Reading file: {file_path}")
        if file_path.startswith('s3://'):
            self.__read_file_from_s3(file_path)
        elif file_path.startswith('http') or file_path.startswith('https'):
            response = requests.get(file_path)
            self.contents = response.text
        else:
            self.contents = read_local_file(file_path)
        return self.contents

    def exists(self, file_location) -> bool:
        """
        This method checks if a file exists.
        :param file_location: The location of the file.
        :return: True if the file exists, False otherwise.
        """
        # Step I: Check if the file is on S3.
        if file_location.startswith('s3://'):
            return self.s3_client.exists(file_location)

        # Step II: Check if the file is a URL.
        elif file_location.startswith('http') or file_location.startswith('https'):
            response = requests.head(file_location)
            return response.status_code == 200

        # Step III: The file is assumed to be local.
        else:
            return os.path.exists(file_location)

    def delete(self, file_path: str) -> None:
        """
        This method deletes a file.
        :param file_path: The path of the file.
        """
        logging.info(f"Deleting file: {file_path}")
        if file_path.startswith('s3://'):
            raise Exception("Deleting files from S3 is not supported.")
        else:
            if os.path.exists(file_path):
                os.remove(file_path)

    def write_file(self, in_file: IO[any], target_file_path: str) -> None:
        # Use write() method to write the contents to the target file.
        self.write(self.read(in_file.name), target_file_path)

    def write(self, contents: str | bytes, file_path: str) -> None:
        """
        This method writes the contents to a file.
        :param contents: The content to write.
        :param file_path: The path of the file.
        """
        logging.info(
            f"Number of characters to write: {len(contents)} to file: {file_path}")
        if file_path.startswith('s3://'):
            tmp_file = tempfile.mkstemp()[1]
            # Check if the contents are bytes.
            if isinstance(contents, bytes):
                # Write the contents to a temp file and upload it to S3.
                with open(tmp_file, 'wb') as f:
                    f.write(contents)
            else:
                # Write the contents to a temp file and upload it to S3.
                with open(tmp_file, 'w') as f:
                    f.write(contents)
            self.s3_client.upload_file(tmp_file, file_path)
        else:
            # Check if the directory exists. If not create it.
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            if isinstance(contents, bytes):
                with open(file_path, 'wb') as f:
                    f.write(contents)
            else:
                with open(file_path, 'w') as f:
                    f.write(contents)

    def __read_file_from_s3(self, file_path: str) -> str:
        """
        This method reads the contents of a file from S3.
        :param file_path:
        :return:
        """
        logging.info(f"Reading file from S3: {file_path}")
        # Get the bucket name and file name.
        file_path_decoded = urllib.parse.unquote(file_path)  # noqa
        # Read the file from S3.
        tmp_file = self.s3_client.get_file(file_path_decoded)
        self.contents = read_local_file(tmp_file)
        # Delete the temp file.
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        return self.contents
