from bs4 import BeautifulSoup
from CustomFormatter import CustomFormatter
import requests
import logging
import time
import sys
import re
import os


logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())

logger.addHandler(ch)


class watchapedia():
    def __init__(self, title=None):
        self._url = 'https://pedia.watcha.com/ko-KR/searches/movies'
        self._movie_urls = []
        self._processed_data = {}

        if isinstance(title, dict) or all(isinstance(x, dict) for x in title):
            self._title = title
        elif title == None:
            pass
        else:
            logging.error('영화제목은 반드시 문자열 타입, 혹은 리스트 타입으로 기입해주시기 바랍니다.')
            sys.exit()

    def getMovieUrl(self):
        if isinstance(self._title, dict):
            movie_title = self._title['title']
            movie_year = self._title['year']
            url = watchapedia.crawlUrl(self._url, movie_title, movie_year)
            if url is not None:
                self._movie_urls.append(url)
                return url
            else:
                logging.error(self._title + '는(은) 왓챠피디아에 등록되어있지 않습니다.')
        elif isinstance(self._title, list):
            excepted_url = []
            for t in self._title:
                movie_title = t['title']
                movie_year = t['year']
                url = watchapedia.crawlUrl(self._url, movie_title, movie_year)
                if url is not None:
                    if url not in self._movie_urls:
                        self._movie_urls.append(url)
                else:
                    excepted_url.append(t)
                    os.system('cls')
                    logging.error(str(excepted_url) + '는(은) 왓챠피디아에 등록되어있지 않습니다.')
            if excepted_url:
                os.system('cls')
                logging.warning(
                    '제외된 영화: ' + str(excepted_url)
                    + '\n총 개수: ' + str(len(excepted_url)) + '개'
                    )
            return url
        else:
            logging.critical('영화제목은 dict 또는 list 타입만 가능합니다.')

    def getMovieData(self):
        processed_data = {}

        if self._movie_urls:
            start = time.time()

            for url in self._movie_urls:
                if url == None:
                    pass
                else:
                    self._processed_data.update(watchapedia.crawlData(url))
                    processed_data.update(watchapedia.crawlData(url))

            end = time.time()

            logger.info(f'{processed_data}\n\nruntime: {end - start:.4f}초')

            return processed_data
        else:
            logging.error("불러올 URL 값이 없습니다. 'getMovieUrl()' 함수를 실행했나요?")

    def crawlUrl(url, movie_title, movie_year) -> str:
        params = {'query': str(movie_title)}
        response = requests.get(url, params=params)
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')

        href = soup.findAll('a', 'css-1aaqvgs-InnerPartOfListWithImage')
        title = soup.findAll('div', 'css-x62r3q')
        year = soup.findAll('div', 'css-h25two')

        for i, j, k in zip(title, year, href):
            i = i.get_text()
            j = j.get_text()

            if movie_title in i:
                if movie_year in j:
                    result = 'https://pedia.watcha.com' + k['href']
                    return result
        else:
            logging.error('movie_title:'+ movie_title + ', movie_year: ' + movie_year +' 이 이름의 url은 없습니다.')

    def crawlData(url):
        logging.debug(type(url))

        if url == None:
            return None
        
        response = requests.get(url)
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')

        # 'css-13h49w0-PaneInner e1svyhwg16'는 영화 데이터를 담은 div의 클래스명이니,
        # 가급적이면 수정하지 말아주세요.
        div = soup.find('div', 'css-13h49w0-PaneInner e1svyhwg16')
        raw_data = []
        if div == None:
            pass
        else:
            for tag in div:
                if '.css' not in str(tag):
                    raw_data.append(tag.get_text())
        
        # 'e5xrf7a0 css-1br354h-VisualUl-PeopleStackableUl'는 감독/출연진 데이터를 담은 ul의 클래스명이니,
        # 가급적이면 수정하지 말아주세요.
        ul = soup.find('ul', 'e5xrf7a0 css-1br354h-VisualUl-PeopleStackableUl')
        li = ul.find_all('a')

        director = []
        main = []

        for tag in li:
            name = str(tag['title'])
            if '감독' in name:
                director.append(name.split('(')[0])
            if '주연' in name:
                main.append(name.split('(')[0])

        return watchapedia.preprocess_data(raw_data, director, main)

    def preprocess_data(raw_data, director, main):
        second_line = raw_data[1].replace(' ', '').split('・')
        third_line = raw_data[2].replace(' ', '').replace(
            '평균★', '').replace(')', '').split('(')

        title = raw_data[0]
        year = second_line[0]
        genres = second_line[1]
        rating = third_line[0]
        views = watchapedia.convert_views(third_line[1])

        result = {title: {'year': year,
                          'genres': genres, 'rating': rating, 'views': views,
                          'director': director, 'main': main}}

        return result

    def convert_views(views):
        # 현재까지는 고려해야 할 경우의 수가 N명, 또는 N만명 밖에 없다.
        if '만' in views:
            return int(re.sub(r'[^0-9]', '', views)) * 10000
        else:
            return int(views.replace('명', '').replace(',', ''))

    @property
    def url(self):
        return self._url

    @property
    def title(self):
        return self._title

    @property
    def movie_urls(self):
        if self._movie_urls:
            return self._movie_urls
        else:
            logging.error("불러올 URL 값이 없습니다. 혹시 'getMovieUrl()' 함수를 실행했나요?")
    
    @property
    def processed_data(self):
        if self._processed_data:
            return self._processed_data
        else:
            logger.error("불러올 영화 데이터 값이 없습니다. 혹시 'getMovieData()' 함수를 실행했나요?")

    @url.setter
    def url(self, url):
        self._url = url

        logger.warning(
            "기본 URL은 'https://pedia.watcha.com/ko-KR/searches/movies'로 설정되어 있습니다.\
            \nURL을 변경하면 오류가 발생할 수 있습니다.\
            \n\n변경된 URL: '" + self._url + "'"
        )

    @title.setter
    def title(self, title):
        if isinstance(title, str) or isinstance(title, list):
            self._title = title
        else:
            logging.error('영화제목은 반드시 문자열 타입, 혹은 리스트 타입으로 기입해주시기 바랍니다.')
            sys.exit()
