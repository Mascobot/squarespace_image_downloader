import logging
import os

from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
import tkinter as tk
from tkinter import filedialog
from urllib.error import URLError, HTTPError
import urllib.request
import xml.etree.ElementTree as ET

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables
xmlfile = ""
folder_selected = ""
MAX_RETRIES = 3
RETRY_DELAY = 5
MAX_WORKERS = 5  # Number of concurrent downloads

window = tk.Tk()
window.title("Squarespace image downloader by @Mascobot")
window.geometry("450x300")
window.config(background="white")

labeltext = tk.StringVar()
labeltext.set("Select XML file and destination folder")

def browse_files():
    global xmlfile
    xmlfile = filedialog.askopenfilename(
        initialdir="/",
        title="Select a File",
        filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
    )
    update_label_text()

def select_destination():
    global folder_selected
    folder_selected = filedialog.askdirectory()
    update_label_text()

def update_label_text():
    if xmlfile and folder_selected:
        labeltext.set("XML file and destination folder have been selected. Ready to start download.")
    elif xmlfile:
        labeltext.set("XML file has been selected. Please select destination folder.")
    elif folder_selected:
        labeltext.set("Destination folder has been selected. Please select XML file.")
    else:
        labeltext.set("Select XML file and destination folder")

def extract_image_urls(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return set([
        elem.text for elem in root.iter()
        if elem.tag == 'link' and elem.text and elem.text.lower().endswith(('.jpg', '.png', '.gif'))
    ])

def download_image(image_url, folder):
    path = os.path.join(folder, image_url.split('/')[-1])
    for attempt in range(MAX_RETRIES):
        try:
            urllib.request.urlretrieve(image_url, path)
            logger.info(f"Successfully downloaded: {image_url}")
            return True
        except (URLError, HTTPError, ConnectionResetError, requests.exceptions.RequestException) as e:
            logger.warning(f"Attempt {attempt + 1} failed for {image_url}. Error: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"Failed to download {image_url} after {MAX_RETRIES} attempts.")
                return False

def download():
    if not xmlfile or not folder_selected:
        labeltext.set("Please select both XML file and destination folder")
        return

    labeltext.set("Downloading images. Please wait...")
    window.update()

    image_urls = extract_image_urls(xmlfile)
    total_images = len(image_urls)
    downloaded_images = 0

    logger.info(f"Starting download of {total_images} images")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(download_image, url, folder_selected): url for url in image_urls}
        for future in as_completed(future_to_url):
            if future.result():
                downloaded_images += 1
            labeltext.set(f"Downloaded {downloaded_images}/{total_images} images")
            window.update()

    labeltext.set(f"Finished downloading {downloaded_images}/{total_images} images")
    logger.info(f"Download complete. Successfully downloaded {downloaded_images} out of {total_images} images.")

# GUI setup
button_explore = tk.Button(window, text="Browse local XML File", command=browse_files)
button_destination = tk.Button(window, text="Select destination folder", command=select_destination)
button_download = tk.Button(window, text="Start download", command=download)
button_exit = tk.Button(window, text="Exit", command=exit)
label = tk.Label(window, textvariable=labeltext)

# Layout
column = 160
button_explore.grid(padx=column, pady=10)
button_destination.grid(padx=column, pady=15)
button_download.grid(padx=column, pady=20)
button_exit.grid(padx=column, pady=25)
label.grid(row=10)

if __name__ == "__main__":
    window.mainloop()
