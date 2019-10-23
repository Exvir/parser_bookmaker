import requests
from bs4 import BeautifulSoup
import re
import csv

class ListReviewsLigaStavok():
    '''
    Получает html страницу и предоставляет методы для парсинга названия букмекерской конторы
    и извлечения списка отзывов на эту контору с сайта bookmaker-ratings.ru
    '''
    def __init__(self, html):
        self.html = html

    @property
    def soup(self):
        return BeautifulSoup(self.html, 'html.parser')

    def get_name_bookmaker(self):
        #получает результат типа "Отзывы о букмекерской конторе {name_bookmaker}""
        full_string = self.soup.find("section", { "class" : "page-block" }).h1.string
        #извлекается имя букмекера
        return re.sub(r'Отзывы о букмекерской конторе ', '', full_string)
    
    def get_list_div(self):
        return self.soup.findAll("div", { "class" : "single" })

class ParserReviewsLigaStavok():
    '''
    Получает супообразный div объект отзыва и предоставляет методы для излечения из него:
    имени автора отзыва, его оценки, текста отзыва, даты, количество лайков и дизлайков отзыва
    '''
    def __init__(self, div):
        self.div = div

    @property
    def get_head(self):
        return self.div.find("div", { "class" : "head" })

    def get_name(self):
        return self.get_head.find("div", { "class" : "name" }).a.string.strip()

    def get_rating(self):
        return self.get_head.find("span", { "class" : "num" }).string

    @property
    def get_content(self):
        return self.div.find("div", { "class" : "content" })

    def get_text_comment(self):
        soup_p = self.get_content.find("div", { "class" : "text" }).p
        #Нужно очистить текст от тегов, средствами супа это сделать не получается
        string_p = str(soup_p)
        return re.sub(r'<[pbr/]+>', '', string_p)

    @property
    def get_bottom(self):
        return self.div.find("div", { "class" : "bottom" })
   
    def get_date(self):
        soup_div = self.get_bottom.find("div", { "class" : "date" })
        #удаляет ненужны теги, которые иногда присутствуют в дереве супа и не позволяют получить строку
        if soup_div.find('i') != None:
            soup_div.find('i').extract()
        return soup_div.string

    def get_like(self):
        return self.get_bottom.find("a", { "class" : "like" }).string.strip()

    def get_dislike(self):
        return self.get_bottom.find("a", { "class" : "dislike" }).string.strip()


def csv_writer(data):
    with open("test.csv", 'w', encoding='utf-8', newline='') as csv_file:
        fieldnames = data.keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, skipinitialspace=True, dialect='excel', delimiter=';')

        writer.writeheader()
        writer.writerow(data)
 
'''
совершает get запрос по казанному url, возвращает html страницу
'''
def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    html_response = requests.get(url, headers=headers).text
    return html_response 

if __name__ == "__main__":
    url = 'https://bookmaker-ratings.ru/review/obzor-bukmekerskoj-kontory-ligastavok/all-feedbacks/'
    html = get_html(url)
    parser = ListReviewsLigaStavok(html)
    list_div = parser.get_list_div()

    data = dict()
    with open("test.csv", 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['Имя букмекера', 'Источник', 'Имя автора отзыва', 'Оценка', 'Текст отзыва', 'Лайков у отзыва', 'Дизлайков у отзыва', 'Дата публикации'], skipinitialspace=True, dialect='excel', delimiter=';')
        writer.writeheader()
        for div in list_div:
            single_div = ParserReviewsLigaStavok(div)
            data['Имя букмекера'] = parser.get_name_bookmaker()
            data['Источник'] = url
            data['Имя автора отзыва'] = single_div.get_name()
            data['Оценка'] = single_div.get_rating()
            data['Текст отзыва'] = single_div.get_text_comment()
            data['Лайков у отзыва'] = single_div.get_like()
            data['Дизлайков у отзыва'] = single_div.get_dislike()
            data['Дата публикации'] = single_div.get_date()            
            writer.writerow(data)