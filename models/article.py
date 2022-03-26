import requests
import re
from bs4 import BeautifulSoup
import datetime
import database
from connection_pool import get_connection

class Article:
    def __init__(self, url: str, _id: int = None) -> None:

        page = requests.get(url)
        soup = BeautifulSoup(page.content, features='html.parser')

        tag_div = soup.find('div', attrs={'data-testid' : "TagCloudWrapper"})
        if len(soup.find_all('p', class_="paywall")) != 0:
            body_paras = soup.find_all('p', class_="paywall")
        elif len(soup.find_all('div', class_='page-module--article--1MWzq')) != 0:
            body_paras = soup.find_all('div', class_='page-module--article--1MWzq')
        else:
            body_paras = soup.find_all('div', class_='article')

        text = (' ').join([para.text for para in body_paras])

        self.id = _id

        if 'utm_source' in url:
            self.url = url.split('?utm_source')[0]
        else:
            self.url = url

        # self.title
        try:
            self.title = soup.find('h1', attrs={'data-testid': 'ContentHeaderHed'}).text
        except AttributeError:
            # removes double whitespaces in case there's a <br> in the title
            try:
                self.title = (' ').join(soup.find('div', class_='hero-module--hed--2ZrJ0').text.split())
            except AttributeError:
                try:
                    self.title = (' ').join(soup.find('div', class_='c-hed').text.split())
                except AttributeError:
                    self.title = (' ').join(soup.find('h1').text.split())


        # self.author
        # generating lists in case of mutliple authors per article
        try:
            # find bylines in header, to
            header_bylines = [item.find_all('a') for item in soup.find_all('div', class_=re.compile("header__byline"))]
            header_bylines_flat = [item for sublist in header_bylines for item in sublist]
            # list(dict.fromkeys(...)) to remove duplicates while preserving order of original list
            self.author = list(dict.fromkeys([item.text for item in header_bylines_flat]))

            if not self.author:
                raise ValueError
        except ValueError:
            try:
                self.author = [item.find('a').text for item in soup.find_all('div', class_='hero-module--byline--1IMB1')]
                if not self.author:
                    raise ValueError
            except ValueError:
                try:
                    self.author = [item.find('a').text for item in soup.find_all('div', class_="c-byline")]
                    if not self.author:
                        raise ValueError
                except ValueError:
                    try:

                        header_bylines = [item.find_all('a') for item in soup.find_all('span', class_=re.compile("module--bylines"))]
                        header_bylines_flat = [item for sublist in header_bylines for item in sublist]
                        self.author = list(dict.fromkeys([item.text for item in header_bylines_flat]))
                        if not self.author:
                            raise ValueError
                    except ValueError:
                        try:
                            self.author = [item.find('a').text for item in soup.find_all('address', class_=re.compile('contributor-author'))]
                            if not self.author:
                                raise ValueError
                        except ValueError:
                            self.author = [item.text for item in soup.find_all('a', class_=re.compile('byline__name'))]
                            if not self.author:
                                raise ValueError("Byline does not match any known pattern. URL:" + self.url)


        # self.date
        try:
            self.date = soup.find(attrs={'data-testid': 'ContentHeaderPublishDate'}).text
        except AttributeError:
            try:
                self.date = soup.find('div', class_='hero-module--date--2Aizt').text.strip()
            except AttributeError:
                try:
                    self.date = soup.find('div', class_='c-date').text.strip()
                except AttributeError:
                    try:
                        self.date = soup.find('span', class_=re.compile('module--pubDate')).text.strip()
                    except AttributeError:
                        self.date = soup.find('time', class_='op-published').text

        self.date_obj = datetime.datetime.strptime(self.date, '%B %d, %Y').strftime('')


        # self.rubric
        try:
            self.rubric = soup.find('span', class_=re.compile("RubricName")).text.strip()
        except AttributeError:
            try:
                self.rubric = soup.find('div', class_=re.compile('hero-module--rubric')).find('a').text.strip()
            except AttributeError:
                try:
                    self.rubric = (' ').join(soup.find('div', class_='c-rubric').find('a').text.split())
                except AttributeError:
                    try:
                        self.rubric = soup.find('span', class_=re.compile('module--rubric')).find('a').text
                    except AttributeError:
                        self.rubric = soup.find('div', class_="rubric", attrs={'data-source': "subChannel"}).text

        # self.tags
        try:
            self.tags = [item.text for item in list(tag_div.children)[1:]]
        except AttributeError:
            self.tags = None

        self.word_count = len(text.split(' '))
        self.date_added = datetime.datetime.today().strftime('%B %d, %Y')

    def __repr__(self) -> str:
        return f"Article({self.title!r}, {self.author!r},{self.date!r})"

    def save(self):
        with get_connection() as connection:
            new_article_id = database.create_article(connection, self.title, self.author, self.date, self.rubric, self.tags, self.word_count, self.url, self.date_added)
            self.id = new_article_id

    # def add_option(self, option_text: str):
    #    Option(option_text, self.id).save()

    def all() -> list["Article"]:
        with get_connection() as connection:
            articles = database.get_articles(connection)

            # to avoid creating new Article objects and scraping the website again
            # not using [cls(article[7] for article in articles]
            return [(article[1], article[2], article[3]) for article in articles]
