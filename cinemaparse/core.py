"""Модуль содержит Class CinemaParser"""
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
class CinemaParser:
    """Класс CinemaParser работает с фильмами"""
    def __init__(self, town='msk'):
        """Присваивание города."""
        self.town = town
        self.content = []
        self.films = []

    def extract_raw_content(self):
        """Доставание содержимого страницы."""
        page = requests.get('https://{}.subscity.ru/'.format(self.town))
        self.content = page.text

    def print_raw_content(self):
        """Возвращение содержимого страницы"""
        print(self.content)

    def get_films_list(self):
        """Возвращение списка фильмов"""
        soup = BeautifulSoup(self.content, 'html.parser')
        arr = soup.find_all(class_="movie-plate")
        self.films = [elem.get("attr-title") for elem in arr]

    def get_film_nearest_session(self, film):
        """Возвращение кинотеатра и ближайшего сеанса фильма"""
        page = requests.get('https://{}.subscity.ru/'.format(self.town))
        soup = BeautifulSoup(page.text, 'html.parser')
        names = soup.find_all(class_="movie-plate")
        for name in names:
            if name.get('attr-title') == film:
                url = 'https://{}.subscity.ru/'.format(self.town)\
                                                                  + name.find('a').get('href')
                page = requests.get(url)
                soup = BeautifulSoup(page.text, 'html.parser')
                cinemas = soup.find_all(class_="row-entity")
                time_cinema = dict()
                for cinema in cinemas:
                    for cur_time in cinema.find_all(class_='text-center cell-screenings'):
                        cur_time = int(cur_time.get('attr-time'))
                        name = cinema.find(class_='underdashed').text
                        if time.time() < cur_time:
                            time_cinema[cur_time + 3600 * 3] = name
                time_cinema = sorted(time_cinema.items(), key=lambda key: key[0])
                earliest = datetime.utcfromtimestamp(time_cinema[0][0])
                now = datetime.today().strftime('%x')
                if earliest.strftime('%x') != now or len(time_cinema) == 0:
                    return None, None
                return time_cinema[0][1], earliest.strftime('%H:%M')
        return None, None

    def get_soonest_session(self):
        """Возвращение ближайшего сеанса, кинотеатра и названия фильма"""
        self.get_films_list()
        film_time = dict()
        for film in self.films:
            name, times = self.get_film_nearest_session(film)
            if times is not None:
                film_time[times] = (film, name)
        film_time = sorted(film_time.items(), key=lambda key: key[0])
        if len(film_time) is False:
            return(None, None, None)
        return film_time[0][1][1], film_time[0][1][0], film_time[0][0]
