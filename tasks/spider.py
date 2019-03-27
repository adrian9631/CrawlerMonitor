import json
import time
import re
import requests
from lxml import html
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from .worker import app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# author: adrian_young
# github: https://github.com/adrianyoung/
# description: adapted to celery

def init_cookies(cookies):
    cookieJar = requests.cookies.RequestsCookieJar()
    for key, value in cookies.items():
        cookieJar.set(key, value)
    return cookieJar

def set_cookies(headers, cookieJar):
    if 'Set-Cookies' in headers.keys():
        for cookie in headers['Set-Cookies'].split(';'):
            key, value = cookie.split('=')[0], cookie.split('=')[1]
            cookieJar.set(key, value)
    return { key:value for key,value in cookieJar.items() }

# request homepage and get cookies
@app.task(ignore_result=False)
def get_cookies():

    headers1 = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Host':'xueqiu.com',
        'Upgrade-Insecure-Requests':'1',
    }

    sess = requests.Session()
    sess.get('https://xueqiu.com', headers=headers1, timeout=200, verify=False)

    return { key:value for key,value in sess.cookies.items() }

# crawl comments linked with stock symbol
@app.task(ignore_result=True)
def comment(cookies, symbol):

    headers3 = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Host':'xueqiu.com',
        'X-Requested-With':'XMLHttpRequest',
    }
    params = {
        'count':'10',
        'comment':'0',
        'hl':'0',
        'source':'all',
        'sort':'time',
        'q':'',
    }
    headers3['Referer'] = 'https://xueqiu.com/S/'+ symbol
    params['symbol'] = symbol
    url = 'https://xueqiu.com/statuses/search.json'
    cookieJar = init_cookies(cookies)

    # replace with backend storage and use send_task function get parser separated with workers

    for i in range(100):
        params['page'] = i+1
        results = requests.get(url, params=params, headers=headers3, cookies=cookieJar, timeout=200, verify=False)
        set_cookies(results.headers, cookieJar)
        logger.info("Now its in the i th page".format(i+1))

        r = json.loads(results.text)
        comments_list = r['list']
        params['last_id'] = comments_list[-1]['id']
        for line in comments_list:
            app.send_task('tasks.spider.parse_comment', [line,], queue='parse_queue')
        time.sleep(2)

# crawl article linked with category
@app.task(ignore_result=True)
def article(cookies, category):

    headers2 = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Host':'xueqiu.com',
        'Referer':'https://xueqiu.com',
        'X-Requested-With':'XMLHttpRequest',
    }

    params = {'since_id':'-1','max_id':'-1','count':'10'}
    params['category'] = category
    url = 'https://xueqiu.com/v4/statuses/public_timeline_by_category.json'
    cookieJar = init_cookies(cookies)

    # replace with backend storage and use send_task function get parser separated with workers

    for i in range(50):
        try:
            results = requests.get(url, params=params, headers=headers2, cookies=cookieJar, timeout=200, verify=False)
            cookies = set_cookies(results.headers, cookieJar)
        except:
            break

        r = json.loads(results.text)
        article_list = r['list']

        for article in article_list:
            app.send_task('tasks.spider.run_article', [article, cookies], queue='crawl_queue')
            time.sleep(2)

        params['max_id'] = r['next_max_id']
        params['count'] = 15

        time.sleep(2)

# separate the crawling part
@app.task()
def run_article(article, cookies):

    headers1 = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Host':'xueqiu.com',
        'Upgrade-Insecure-Requests':'1',
    }

    cookieJar = init_cookies(cookies)
    article = json.loads(article['data'])
    article_id = article['target']
    article_url = 'https://xueqiu.com' + article_id
    result = requests.get(article_url, headers=headers1, cookies=cookieJar, timeout=200, verify=False)
    app.send_task('tasks.spider.parse_article', [article, result.text], queue='parse_queue')

# parse article response with regex
@app.task()
def parse_article(article, text):

    date = ''.join(re.findall('"timeBefore":"(.*?)"', text, re.S))
    text = ''.join(re.findall("<p>(.*?)</p>", text, re.S))
    text = re.sub('(<)?a href.*?</a>(&nbsp;)?', '', text)
    text = re.sub('<.*?>', '', text)

    info_dict = {}
    info_dict['target'] =article['target']
    info_dict['title'] = article['title']
    info_dict['text'] = text
    info_dict['date'] = date

    return info_dict

# parse comment response with regex and xpath
@app.task()
def parse_comment(comment):

    info_dict = {}
    info_dict['id'] = comment['id']
    info_dict['user_id'] = comment['user_id']
    info_dict['description'] = html.fromstring(comment['description']).xpath('string(.)')
    info_dict['text'] = html.fromstring(comment['text']).xpath('string(.)')
    info_dict['source'] = comment['_source']

    return info_dict

