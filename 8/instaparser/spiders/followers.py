import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy



class InstagramSpider(scrapy.Spider):
    name = 'followers'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com']
    insta_login = 'globalkingofusers@gmail.com'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:10:1595094806:AdVQANUj7i9oneF4KHAe2X0nNKXfWnZN2EWIZPbw+Z70eQNMseyf1XicDHCWKX21kiDwc27mHCY6dc258TwZLe9C3c2+svdDAOuOkj+dnYvT8Z4Mqff+517wBjpDae5U6kPSlmQdvlLg9eK5PFI='
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_users = ['ai_machine_learning','antonioap']      #Пользователь, у которого собираем посты. Можно указать список

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    folowers_hash = 'c76146de99bb02f6415203be841dd25a'     #hash для получения данных по постах с главной страницы
    parse_hash = 'd04b0a864b4b54837c0d870b0e77e076'
    
    def parse(self, response):
        csrf_token = self.fetch_csrf_token(response.text)   #csrf token забираем из html
        yield scrapy.FormRequest(                   #заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username':self.insta_login, 'enc_password':self.insta_pwd},
            headers={'X-CSRFToken':csrf_token}
        )
        
    def user_parse(self, response:HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for parse_user in self.parse_users:  
                yield response.follow(                  #Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                    f'/{parse_user}',
                    callback= self.user_data_parse,
                    cb_kwargs={'username':parse_user}
                )

    def user_data_parse(self, response:HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)       #Получаем id пользователя
        variables={'id':user_id,                                    #Формируем словарь для передачи даных в запрос
                   'first':50}                                      #12 постов. Можно больше (макс. 50)
        url_posts = f'{self.graphql_url}query_hash={self.parse_hash}&{urlencode(variables)}'    #Формируем ссылку для получения данных о постах
        yield response.follow(
            url_posts,
            callback=self.user_posts_parse,
            cb_kwargs={'username':username,
                       'user_id':user_id,
                       'variables':deepcopy(variables)}         #variables ч/з deepcopy во избежание гонок
        )

    def user_posts_parse(self, response:HtmlResponse,username,user_id,variables):   #Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):                                          #Если есть следующая страница
            variables['after'] = page_info['end_cursor']                            #Новый параметр для перехода на след. страницу
            url_posts = f'{self.graphql_url}query_hash={self.parse_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_posts_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        users = j_data.get('data').get('user').get('edge_follow').get('edges')     #Сами посты
        for user in users:                                                                      #Перебираем посты, собираем данные
            item = InstaparserItem(
                user_id = user_id,
                user_name = username,
                target_id = user['node']['id'],
                target_name = user['node']['full_name'],
                photo = user['node']['profile_pic_url']
            )
        yield item                  #В пайплайн





    #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')