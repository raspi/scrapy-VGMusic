import os
from pathlib import Path
from shutil import move
from tempfile import NamedTemporaryFile

import scrapy

from vgmusic.items import *

def validatechars(s: str) -> str:
    """
    Filesystem friendly
    :param s:
    :return:
    """

    s = s.replace(r"\\", "_")
    s = s.replace(r"/", "_")
    s = s.replace(r"?", "_")
    return s

class VgmusicPipeline:
    def process_item(self, item: Item, spider: scrapy.Spider):
        if not isinstance(item, Item):
            spider.log("Invalid item type")
            return

        filename = None
        basepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'items'))

        if isinstance(item, Tune):
            if item.data is None:
                spider.logger.info(f"Data is none")
                return

            if len(item.data) == 0:
                spider.logger.info(f"No data")
                return

            nitem = item
            # Remove filesystem unfriendly characters
            nitem.artist = validatechars(nitem.artist)
            nitem.title = validatechars(nitem.title)
            nitem.system = validatechars(nitem.system)
            nitem.game = validatechars(nitem.game)

            filename = f"{nitem.game} - {nitem.artist} - {nitem.title} ({nitem.uploadtime}).mid"
            basepath = os.path.join(basepath, nitem.system)

        if filename is None:
            raise ValueError("No filename")

        if not os.path.isdir(basepath):
            Path(basepath).mkdir(parents=True, exist_ok=True)

        # Save to temporary file
        tmpf = NamedTemporaryFile("wb", prefix="vg-", suffix=f".mid", delete=False)
        with tmpf as f:
            f.write(item.data)
            f.flush()
            spider.logger.info(f"saved as {f.name}")

        # Rename and move the temporary file to actual file
        newpath = move(tmpf.name, os.path.join(basepath, filename))
        spider.logger.info(f"renamed {tmpf.name} to {newpath}")
