import json
import os
import re
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
        self.Name = str()
        self.Title = str()
        self.ComicURL = str()
        self.ImageURL = str()
        self.Filename = str()


class ComicStripInfo:

    def __init__(self):
        self.name = str()
        self.website = str()
        self.feed_url = str()
        self.comic_url = str()
        self.image_selector = str()
        self.image_url_prefix = str()
        self.prev_comic_selector = str()
        self.prev_url_prefix = str()
        self.prev_comic = str()  # url of prev comic


class ComicSource:  # iterable class which will provide the list of comics from a given source

    max_length = Globals.ImageItems

    def __init__(self, source_info: ComicStripInfo):
        self.source = source_info
        self.comics = []
        self.current = -1

        if self.source.feed_url == '':
            self.comics = get_comics(self.source)
            print('getting from web-pages')
        else:
            print('getting from feed')
            self.comics = get_comics_from_feed(self.source)

    def __iter__(self):
        self.current = -1
        return self

    def __next__(self):
        self.current += 1
        # download next comic
        if self.current < len(self.comics) and self.current < self.max_length:
            if download_image(self.comics[self.current]):
                print('Downloaded ', self.comics[self.current].Filename)
                return self.comics[self.current]
            else:
                print('Image not found skipping...')
                return next(self)
        else:
            raise StopIteration


def add_source_data(comic_info: ComicStripInfo):
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


def get_source_data():
    '''
    :return: ComicStripInfo object
    '''

    if os.path.isfile(Globals.JSONFilename):
        with open(Globals.JSONFilename, 'r') as file:
            data = json.load(file, object_hook=decode_object)
            return data
    else:
        return None


def check_url(url: str, return_data=False):
    try:
        html = requests.get(url)

    except requests.exceptions.MissingSchema:
        url = 'http://' + url
        return check_url(url, return_data)

    except Exception as exp:
        return str(exp)

    if return_data:
        return html.status_code, html

    return html.status_code


def download_image(comic: Comic) -> bool:
    print('saving file ', comic.Filename)

    path = os.path.join(Globals.ImageDir, comic.Name)
    if not os.path.exists(path):
        os.makedirs(path)

    path = os.path.join(path, comic.Filename)

    if os.path.exists(path):
        print('Image file exits, loading ...')
        comic.Filename = path
        return True

    img_data = check_url(comic.ImageURL, True)

    if isinstance(img_data, int) or isinstance(img_data, str) or img_data is None:
        print('Image url returned status:', img_data)
        return False
    else:
        img_data = img_data[-1].content
        # saving image file
        # path = os.path.join(path, comic.Filename)
        with open(path, 'wb') as buffer:
            buffer.write(img_data)
        comic.Filename = path
        return True


def get_comics(source: ComicStripInfo, length=Globals.ImageItems, save_image=False):
    '''
        downloads length number of comic from one source
    :return: list of Comic object
    '''

    comics = []

    for _ in range(length):

        if source.prev_comic != '':
            source.comic_url = source.prev_url_prefix + source.prev_comic

        try:
            html_request = requests.get(source.comic_url)
            html_request.raise_for_status()
        except Exception as exp:
            print("Issue with the url ", str(exp))
            return

        soup = BeautifulSoup(html_request.text, 'html.parser')
        comic = Comic()

        # getting Image url
        img_path = soup.select(source.image_selector)[0].attrs['src']
        comic.ImageURL = source.image_url_prefix + img_path

        comic.Filename = img_path.split('/')[-1]
        comic.Title = comic.Filename.replace('_', ' ')
        comic.ComicURL = source.comic_url
        comic.Name = source.name

        if save_image:
            download_image(comic)

        # finding prev url
        if source.prev_comic_selector != '':
            source.prev_comic = soup.select(source.prev_comic_selector)[0].attrs['href']

        comics.append(comic)

    return comics


def get_comics_from_feed(source: ComicStripInfo, save_image=False):
    data = check_url(source.feed_url, True)

    if isinstance(data, int) or isinstance(data, str):
        print('url returned status:', data)
        return

    """
    imgurl_regex = re.compile(r'''src="
                                (?:https?)?     #http
                                (?:[://]+)      #://
                                (?:(?:www\.)?     # www
                                (?:\.+ \. \w{3}))? #website name - www. xyz .com
                                (.+\.(?:jpg|png))" ''', re.X)
    """

    imgurl_regex = re.compile(r'src="(?:https?)?(?:[://]+)(.+\.(?:jpg|png))"')

    soup = BeautifulSoup(data[-1].text, 'xml')

    comic_list = []

    items = soup.channel.find_all('item')
    # some comics have 'entry' instead of item: use css selector of rss to navigate

    for item in items:
        comic = Comic()

        # use find(path) where path is the img element to find
        description = item.description.text
        img_links = imgurl_regex.search(description)

        if img_links is not None:
            img_url = img_links.groups()[0]

            img_url = re.sub(r'-\d\d\dx\d\d\d', '', img_url)

            comic.ImageURL = img_url
            # TODO: MEDIUM | if image url has size appended then remove it; use regex->  (xxx(-123x123).ext)

        comic.Title = item.title.text
        comic.ComicURL = item.link.text

        comic.Filename = comic.Title + comic.ImageURL[-4:]
        comic.Name = soup.channel.title.text

        if save_image:
            if not download_image(comic):
                continue

        comic_list.append(comic)

    return comic_list


def verify_new_comics(new_source: ComicStripInfo):
    feed_data = requests.get(new_source.feed_url).text

    soup = BeautifulSoup(feed_data, 'xml')
    item = soup.channel.find('item')
    if item.description.text != '':
        soup = BeautifulSoup(item.description.text, 'xml')
        img_url = soup.find('img')

        # if img_url is not None: check for regex
    # elif item.media


def get_rss_feed(url: str):
    data = check_url(url, True)

    if isinstance(data, int) or isinstance(data, str):
        print('url returned status:', data)
        return

    soup = BeautifulSoup(data[-1].text, 'lxml')

    rss_link = soup.find('link', {'type': 'application/rss+xml'})

    if rss_link is None:
        rss_link = soup.find('link', {'type': 'application/atom+xml'})

    if rss_link is not None:
        rss_link = rss_link.attrs['href']

        if 'http' not in rss_link:  # fix relative url
            rss_link = url + rss_link

    return rss_link  # return type (rss or atom)


def add_new_comic(**kwargs):
    # TODO: MEDIUM | get details; test this part

    if 'website' in kwargs:
        new_source = ComicStripInfo()
        website_url = kwargs['website'].split(':')[-1].replace('/', '')
        website_url = 'http://' + website_url
        url_status = check_url(website_url)

        if url_status == 200:
            new_source.website = website_url

            if 'feed' in kwargs:
                feed_url = kwargs['feed'].split(':')[-1].replace('//', '')
                feed_url = 'http://' + feed_url
            else:
                feed_url = get_rss_feed(website_url)

            if feed_url is not None:

                feed_url_status = check_url(feed_url)

                if feed_url_status == 200:
                    new_source.feed_url = feed_url
                    # TODO: low | check image links in rss

                else:
                    print('feed not reachable \n url returned:', feed_url_status)
            else:
                print("feed url not found on website header. ")
        else:
            print('website returned:', url_status)

        print(new_source.website, new_source.feed_url)

        new_source.name = new_source.website[:-4]

        return new_source


if __name__ == '__main__':

    while True:

        website = input("website: ")
        newSource = add_new_comic(website=website)
        print(newSource.name, newSource.feed_url, newSource.website)

        for ci in get_comics_from_feed(newSource):
            print(ci.Name, ci.ImageURL, ci.Filename, ci.Title, ci.ComicURL)
