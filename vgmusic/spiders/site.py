import os
from datetime import datetime
from urllib.parse import urlsplit, urlencode, SplitResult
from urllib.parse import parse_qsl as queryparse
import scrapy

from vgmusic.items import Tune


class SiteSpider(scrapy.Spider):
    allowed_domains: list = [
        'vgmusic.com',
        'www.vgmusic.com',
    ]

    start_urls: list = [
        'https://vgmusic.com/',
    ]

    def parse(self, response: scrapy.http.Response):
        pass


class NewFilesSpider(SiteSpider):
    name = 'new'

    def __init__(self):
        self.start_urls = [
            'https://vgmusic.com/new-files/index.php?page=1&s1=date&sd1=1',
        ]

    def parse(self, response: scrapy.http.Response):
        """
        Get file list
        :param response:
        :return:
        """

        u: SplitResult = urlsplit(response.url)
        q: dict = dict(queryparse(u.query))

        max_page = max(list(map(int, response.xpath(
            "/html/body/table/tr/td[@class='button']/form/input[@name='page']/@value"
        ).getall())))
        current_page = int(q['page'])

        if current_page < max_page:
            # Call next page
            q['page'] = str(current_page + 1)
            yield scrapy.Request(
                response.urljoin("?" + urlencode(q)),
                callback=self.parse,
            )

        for row in response.xpath("/html/body/table[@width='100%']/tr[@class='newfiles']"):
            # Iterate through uploaded files
            link = row.xpath("./td[4]/a/@href").get()
            song = row.xpath("./td[4]/a/text()").get()
            if song is None:
                # Use file name
                song = os.path.basename(urlsplit(link).path)

            sequencer = row.xpath("./td[5]/text()").get()
            if sequencer is None:
                sequencer = "Unknown"

            game = row.xpath("./td[3]/text()").get()
            if game is None:
                game = "Unknown"

            uploadtime = datetime.strptime(row.xpath("./td[1]/text()").get(), "%Y-%m-%d %H:%M:%S")
            system = row.xpath("./td[2]/text()").get()

            yield scrapy.Request(
                response.urljoin(link),
                callback=self.dl_midi,
                meta={
                    "tune": Tune(
                        artist=sequencer,
                        title=song,
                        system=system,
                        game=game,
                        uploadtime=uploadtime,
                        data=None,
                    ),
                },
            )

    def dl_midi(self, response: scrapy.http.Response):
        """
        Download MIDI file
        :param response:
        :return:
        """

        ctype = response.headers.get('Content-Type').decode('utf-8')
        if ctype != 'audio/midi':
            raise ValueError(f"Invalid content-type '{ctype}'")

        tune: Tune = response.meta["tune"]
        tune.data = response.body
        yield tune
