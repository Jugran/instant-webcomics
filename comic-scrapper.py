#!/usr/bin/env python3
import sys

import ComicManager
import SourceManager

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # TODO add sys arguments support
        pass

    if input("Add comic strips sources?[y|n] ") == 'y':
        SourceManager.add_new_comic()

    if input("Load comics? [y|n]") == 'y':
        comicManger = ComicManager.ComicManager(length=1)
