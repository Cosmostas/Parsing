from bs4 import BeautifulSoup as bs
import requests
import numpy as np
from pprint import pprint
from pymongo import MongoClient

def find_offer(offer_text):
        min_offer = np.nan
        max_offer = np.nan
        currency = np.nan
        
        offer_text = offer_text.replace(chr(160),'')
        offer_text = offer_text.replace(chr(32),'')
        offer_text = offer_text.replace('.','')

        digits = '0123456789'
        
        if offer_text.find('от') > -1:
            offer_text = offer_text.replace('от','')
            for i in range(0, len(offer_text)):
                if (offer_text[i] not in digits):
                    cur_pos = i
                    break
            min_offer = int(offer_text[0:cur_pos])
            currency = offer_text[cur_pos:]

        elif offer_text.find('до') > -1:
            offer_text = offer_text.replace('до','')
            for i in range(0, len(offer_text)):
                if (offer_text[i] not in digits):
                    cur_pos = i
                    break
            max_offer =  offer_text[0:cur_pos]
            currency = offer_text[cur_pos:]
            
        elif offer_text.find('-') > -1:
            sep_pos = offer_text.find('-')
            min_offer = int(offer_text[0:sep_pos])

            for i in range(sep_pos + 1, len(offer_text)):
                if (offer_text[i] not in digits):
                    cur_pos = i
                    break
            max_offer = int(offer_text[sep_pos + 1:cur_pos])
            currency = offer_text[cur_pos:]

        elif offer_text.find('По договоренности') > -1:
            pass
        return min_offer, max_offer, currency


def parse_hh(vacancy_name, Num_of_Pages):
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
          'Accept':'*/*'}



    domain_url = 'https://hh.ru'

    local_url = '/search/vacancy'

    text = vacancy_name
    L_save_area = 'true'
    st = 'searchVacancy'
    fromSearch = 'true'
    page = '1'

    params = {
    'L_save_area' : L_save_area,
    'text' : text,
    'st' : st,
    'fromSearch' : fromSearch,
    'page' : page}

    is_last_page = False
    counter = 0

    while not is_last_page and counter < Num_of_Pages:


        response = requests.get(domain_url + local_url, headers = header, params=params)

        soup = bs(response.text, 'html.parser')
        
        block_class = 'vacancy-serp'
        elem_class = 'vacancy-serp-item'

        jobs_block = soup.find('div', {'class' : block_class})   
        jobs_list = jobs_block.find_all('div', {'class': elem_class})
        

        jobs = []
        for job in jobs_list:
            job_data = {}
            name = job.find('a', {'data-qa' : 'vacancy-serp__vacancy-title'}).getText()

            href = job.find('a', {'data-qa' : 'vacancy-serp__vacancy-title'})['href']

            offer = job.find('span', {'data-qa' : 'vacancy-serp__vacancy-compensation'})
            if offer:
                offer = offer.getText()
                min_offer, max_offer, currency = find_offer(offer)

            else:
                min_offer = np.nan
                max_offer = np.nan
                currency = np.nan

            employer = job.find('a', {'data-qa' : 'vacancy-serp__vacancy-employer'}).getText().strip()
            city = job.find('span', {'data-qa' : 'vacancy-serp__vacancy-address'}).getText()

            _id = parse_id(href, True)

            job_data['_id'] = _id
            job_data['name'] = name
            job_data['min_offer'] = min_offer
            job_data['max_offer'] = max_offer
            job_data['currency'] = currency
            job_data['employer'] = employer
            job_data['city'] = city   
            job_data['href'] = href
            job_data['resource '] = 'hh.ru'

            jobs.append(job_data)

        next_page_tag = soup.find('a', {'data-qa' : 'pager-next'})

        if next_page_tag == None:
            is_last_page = True
        else:
            local_url = next_page_tag['href']
            counter += 1
    return jobs


def parse_superjob(vacancy_name, Num_of_Pages):

    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
          'Accept':'*/*'}



    domain_url = 'https://russia.superjob.ru'

    local_url = '/vacancy/search/'

    
    keywords = vacancy_name

    is_last_page = False
    counter = 0


    params = {
        'keywords' : keywords}

    while not is_last_page and counter < Num_of_Pages:

        response = requests.get(domain_url + local_url, headers = header, params=params)

        soup = bs(response.text, 'html.parser')
        
        elem_class = '_3zucV _1fMKr undefined _1NAsu'

        jobs_list = soup.find_all('div', {'class': elem_class})



        jobs = []
        for job in jobs_list:

            job_data = {}
            block = job.find('div', {'class' : 'jNMYr GPKTZ _1tH7S'})
            if block is None:
                continue
            name = block.find('div', {'class' : '_3mfro PlM3e _2JVkc _3LJqf'}) 
            href = name.find('a')['href']
            name = name.getText() 
            offer = block.find('span', {'class' : '_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'}).getText()
            min_offer, max_offer, currency = find_offer(offer)
            
            block = job.find('div', {'class' : '_3_eyK _3P0J7 _9_FPy'})
            employer = block.find('span', {'class' : '_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _2VHxz _15msI'})
            city = block.find('span', {'class' : '_3mfro f-test-text-company-item-location _9fXTd _2JVkc _2VHxz'})
            if employer is None:
                employer = np.nan
            else:
                employer = employer.getText()
            
            if city is None:
                city = np.nan
            else:
                city = city.getText()[8:]

            _id = parse_id(href, False)

            job_data['_id'] = _id
            job_data['name'] = name
            job_data['min_offer'] = min_offer
            job_data['max_offer'] = max_offer
            job_data['currency'] = currency
            job_data['employer'] = employer
            job_data['city'] = city   
            job_data['href'] = href
            job_data['resource '] = 'superjob.ru'
            
            jobs.append(job_data)

        next_page_tag = soup.find('a', {'class': 'icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-Dalshe'})

        if next_page_tag == None:
            is_last_page = True
        else:
            local_url = next_page_tag['href']
            counter += 1
    return(jobs)

# Извлечение id из ссылки на страницу с вакансией
def parse_id(href, is_parse_hh):

    if is_parse_hh:
        id = ""
        id_begin = href.find('vacancy/') + 8
        for i in range (id_begin,len(href)):
            if href[i] == "?":
                break
            id += href[i]
    else:
        id = ""
        id_end = href.find('.html') - 1
        for i in range (id_end,0,-1):
            if href[i] == "-":
                break
            id += href[i]
        id = id[::-1]
    return id

# Задание №3. Вставка новых значений(уникальных) в бд
def insert_into_collection(collection, data):
    for job in data:
        collection.update(job, {'upsert' : True})

# Задание №2. Поиск в бд записей с зар. платой больше необходимой
def offer_search(collection, required_offer):
    required_jobs = collection.find( { '$or' : [ { 'min_offer' : { '$gt' : required_offer } }, { 'max_offer' : { '$gt' : required_offer } } ] } )
    for job in required_jobs:
        pprint(job)

def main(): 
    Num_of_Pages = 1
    vacancy_name = 'Программист'

    client = MongoClient('localhost', 27017)
    db = client['vacancy']

    hh = db.hh
    hh.drop({})
    superjob = db.superjob
    superjob.drop({})

    jobs = []
    jobs += (parse_hh(vacancy_name,Num_of_Pages))
    hh.insert_many(jobs)

    
    jobs = []
    jobs += (parse_superjob(vacancy_name,Num_of_Pages))
    superjob.insert_many(jobs)

    offer_search(hh,50000)
    print(1)
if __name__ == "__main__":
    main() 