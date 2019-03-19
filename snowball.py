import json
import time
import re
import requests
from lxml import html
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# author: adrian_young
# github: https://github.com/adrianyoung/
# description: the project, crawling the article and comments in Snow Ball, has simple structure without anti-spider processing.

# store in json format
def dump(data, path):
    with open(path, 'w', encoding='utf-8') as fp:
        json.dump(data, fp)

# crawl comments linked wihh stock symbol
def comment(sess, symbol):

    headers3 = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Host':'xueqiu.com',
        'X-Requested-With':'XMLHttpRequest',
    }

    url = 'https://xueqiu.com/statuses/search.json'
    headers3['Referer'] = 'https://xueqiu.com/S/'+ symbol
    params = {
        'count':'10',
        'comment':'0',
        'hl':'0',
        'source':'all',
        'sort':'time',
        'q':'',
    }
    params['symbol'] = symbol

    items = []
    for i in range(100):
        params['page'] = i+1
        results = sess.get(url, params=params, headers=headers3, timeout=200, verify=False)
        r = json.loads(results.text)
        comments_list = r['list']
        params['last_id'] = comments_list[-1]['id']
        for line in comments_list:
            info_dict = parse_comment(line)
            items.append(info_dict)
        time.sleep(2)

    return items

# crawl article linked with category
def article(sess, category):

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

    headers1 = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Host':'xueqiu.com',
        'Upgrade-Insecure-Requests':'1',
    }

    items = []

    url = 'https://xueqiu.com/v4/statuses/public_timeline_by_category.json'
    params = {'since_id':'-1','max_id':'-1','count':'10'}
    params['category'] = category

    #while True:
    for i in range(2):
        try:
            results = sess.get(url, params=params, headers=headers2, timeout=200, verify=False)
        except:
            break

        r = json.loads(results.text)
        article_list = r['list']
        for article in article_list:
            article = json.loads(article['data'])
            article_id = article['target']
            article_url = 'https://xueqiu.com' + article_id
            result = sess.get(article_url, headers=headers1, timeout=200, verify=False)
            info_dict = parse_article(article, result)
            items.append(info_dict)
            time.sleep(2)

        params['max_id'] = r['next_max_id']
        params['count'] = 15
        time.sleep(2)

    return items

# parse article response with regex
def parse_article(article, result):

    text = ''.join(re.findall("<p>(.*?)</p>", result.text, re.S))
    text = re.sub('(<)?a href.*?</a>(&nbsp;)?', '', text)
    text = re.sub('<.*?>', '', text)

    date = ''.join(re.findall('"timeBefore":"(.*?)"', result.text, re.S))

    info_dict = {}
    info_dict['target'] =article['target']
    info_dict['title'] = article['title']
    info_dict['text'] = text
    info_dict['date'] = date

    return info_dict

# parse comment response with regex and xpath
def parse_comment(comment):

    info_dict = {}
    info_dict['id'] = comment['id']
    info_dict['user_id'] = comment['user_id']
    info_dict['description'] = html.fromstring(comment['description']).xpath('string(.)')
    info_dict['text'] = html.fromstring(comment['text']).xpath('string(.)')
    info_dict['source'] = comment['_source']

    return info_dict

# request homepage and get cookies
def get_session():

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
    return sess

# simplify the crawler process
def crawler(sess, params, func, path):

    data_list = []
    for param in params:
        data_list.extend(func(sess, param))

    dump(data_list, path)

if __name__ == '__main__':

    # crawler seeds
    symbols = ['TSLA']
    categorys = ['111']
    #categorys = ['105','111','102','104','101','113','114','110']

    # storage path
    comment_path = './comment.json'
    article_path = './article.json'

    # run crawlers
    sess = get_session()
    crawler(sess, symbols, comment, comment_path)
    crawler(sess, categorys, article, article_path)

