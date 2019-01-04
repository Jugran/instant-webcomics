from typing import List

import Globals
import SourceManager


class ComicManager:

    comicList: List[SourceManager.Comic] = []
    sourceList: List[SourceManager.ComicStripInfo] = []
    currentComic = -1

    def __init__(self, length=Globals.ImageItems):
        '''
        :param length: Number of comic from each source
        '''

        self.sourceList = SourceManager.read_json()
        self.comicList = self.load_comics(length)

        print('comics loaded')

    def load_comics(self, length=Globals.ImageItems):
        print('Loading Comics ...')
        comics = []

        for source in self.sourceList:
            comic = SourceManager.download_comic(source, length)
            comics.append(comic)

        return comics

    def get_comic(self, comic_index=0):
        comic = self.comicList[comic_index]
        self.currentComic = comic_index
        return comic

    def get_next(self):
        if self.currentComic < len(self.comicList):
            self.currentComic += 1
            return self.comicList[self.currentComic]
        else:
            self.load_comics()

    def get_prev(self):
        if self.currentComic > 0:
            self.currentComic -= 1
            return self.comicList[self.currentComic]


