import json
import os

import requests
from bs4 import BeautifulSoup

import Globals


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ComicStripInfo):
            return o.__dict__

        super().default(self, o)


def decode_object(o):
    data = ComicStripInfo()
    data.__dict__ = o
    return data


class Comic:

    def __init__(self):
        self.Title = str()
        self.Website = str()
        self.ComicURL = str()
        self.ImageURL = str()
        self.Filename = str()


class ComicStripInfo:

    def __init__(self):
        self.name = str()
        self.website = str()
        self.comic_url = str()
        self.image_cssSelector = str()
        self.image_url_prefix = str()
        self.prev_comic_cssSelector = str()
        self.prev_url_prefix = str()
        self.prev_comic = str()  # url of prev comic


def add_to_json(comic_info: ComicStripInfo):
    if os.path.isfile(Globals.JSONFilename):
        with open(Globals.JSONFilename, 'a+') as file:
            file.seek(0, os.SEEK_END)
            file.seek(file.tell() - 2, os.SEEK_SET)
            file.truncate()

            file.write(',')
            json_out = json.dumps([comic_info], indent=4, cls=CustomJSONEncoder)

            file.write(json_out[1:-1])
            file.write(']')
    else:
        with open(Globals.JSONFilename, 'w') as file:
            json.dump([comic_info], file, indent=4, cls=CustomJSONEncoder)


def read_json():
    '''
    :return: list of ComicStripInfo objects
    '''

    if os.path.isfile(Globals.JSONFilename):
        with open(Globals.JSONFilename, 'r') as file:
            data = json.load(file, object_hook=decode_object)
        return data
    else:
        return []


def download_comic(source: ComicStripInfo, length=Globals.ImageItems) -> Comic:
    '''
        downloads length number of comic from one source
    :return: list of Comic object
    '''

    comics = []
    if not os.path.isdir(Globals.ImageDir):
        os.mkdir(Globals.ImageDir)

    for _ in range(length):

        if source.prev_comic != '':
            source.comic_url = source.prev_url_prefix + source.prev_comic

        try:
            html_request = requests.get(source.comic_url)
            html_request.raise_for_status()
        except:
            print("Issue with the url")
            return

        soup = BeautifulSoup(html_request.text, 'html.parser')
        comic = Comic()

        # getting Image url
        img_path = soup.select(source.image_cssSelector)[0].attrs['src']
        comic.ImageURL = source.image_url_prefix + img_path

        comic.Filename = img_path.split('/')[-1]
        comic.Title = comic.Filename.replace('_', ' ')
        comic.Website = source.website
        comic.ComicURL = source.comic_url

        img_data = requests.get(comic.ImageURL).content

        # saving image fileList[SM.Comic]
        with open(Globals.ImageDir + comic.Filename, 'wb') as buffer:
            buffer.write(img_data)

        # finding prev url
        if source.prev_comic_cssSelector != '':
            source.prev_comic = soup.select(source.prev_comic_cssSelector)[0].attrs['href']

        comics.append(comic)

    return comics


def add_comic_details():
    comic_info = ComicStripInfo()

    # TODO: get details
    add_to_json(comic_info)
