import SourceManager


class ComicManager:
    comicList = []  # mixed list of comics from all sources
    comicSourceList = []
    currentComic = -1

    def __init__(self):
        self.load_comics()

        print('comics loaded')

    def load_comics(self):
        source_data = SourceManager.get_source_data()
        for sd in source_data:
            comic_source = SourceManager.ComicSource(sd)
            self.comicSourceList.append(comic_source)

    def get_comic(self, comic_index=0) -> SourceManager.Comic:
        comic = self.comicList[comic_index]
        self.currentComic = comic_index
        return comic

    def get_next(self, source_index=0) -> SourceManager.Comic:

        if self.currentComic + 1 >= len(self.comicList):
            # load new comic
            try:
                new_comic = next(self.comicSourceList[source_index])
                self.comicList.append(new_comic)
                self.currentComic += 1
                return new_comic

            except StopIteration:  # end of current source comic entries
                source_index += 1
                if source_index < len(self.comicSourceList):
                    return self.get_next(source_index)

        else:
            self.currentComic += 1
            return self.comicList[self.currentComic]

    def get_prev(self) -> SourceManager.Comic:
        if self.currentComic > 0:
            self.currentComic -= 1
            return self.comicList[self.currentComic]
