import requests
from bs4 import BeautifulSoup
import json
import re
import jieba
import time
import urllib.request
import urllib.parse
import urllib.error
from urllib.parse import urljoin

USER_AGENT = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) '
                            'Chrome/20.0.1092.0 Safari/536.6'}

URL_TIMEOUT = 10
SLEEP_TIME = 1

dict_result = {}
list_search_result = []

#url列表获取，此处只深搜一层，可改range(1)中的参数
def crawl(pages):
    for i in range(1):
        newpages=set()
        for page in pages:
            try:
                res = requests.get(page)      
            except:
                print ("Could not open %s" % page) 
                continue
            html = res.text  #解析为文本数据
            soup = BeautifulSoup(html,'html.parser')

            links=soup('a') #找所有链接
            for link in links:
                if('href' in dict(link.attrs)):
                    url=urljoin(page,link['href'])
                    if url.find("'")!=-1:continue
                    url=url.split('#')[0]
                    if url[0:4]=='http':   
                        newpages.add(url)                   
        pages=list(newpages)
        pages.sort()
    return pages


def crawler(list_URL):
    for i, url in enumerate(list_URL):
        print("网页爬取:", url, "...")
        page = requests.get(url, headers=USER_AGENT, timeout=URL_TIMEOUT)
        page.encoding = page.apparent_encoding  # 防止编码解析错误
        result_clean_page = bs4_page_clean(page)
        result_chinese = re_chinese(result_clean_page)
        soup = BeautifulSoup(page.text, 'lxml')
        try:
            contents=soup.find(attrs={"name": "description"})['content']
        except:
            continue
        dict_result[i + 1] = {"url": url, "word": jieba_create_index(result_chinese), "title":soup.title.text, "content":contents}
        print("爬虫休眠中...")
        time.sleep(SLEEP_TIME)


def bs4_page_clean(page):
    print("正则表达式：清除网页标签等无关信息...")
    soup = BeautifulSoup(page.text, "html.parser")
    [script.extract() for script in soup.findAll('script')]
    [style.extract() for style in soup.findAll('style')]
    reg1 = re.compile("<[^>]*>")
    content = reg1.sub('', soup.prettify())
    return str(content)


def re_chinese(content):
    print("正则表达式：提取中文...")
    pattern = re.compile(u'[\u1100-\uFFFD]+?')
    result = pattern.findall(content)
    return ''.join(result)


def jieba_create_index(string):
    list_word = jieba.lcut_for_search(string)
    dict_word_temp = {}
    for word in list_word:
        if word in dict_word_temp:
            dict_word_temp[word] += 1
        else:
            dict_word_temp[word] = 1
    return dict_word_temp


def search(string):
    for k, v in dict_result.items():
        if string in v["word"]:
            list_search_result.append([v["url"], v["word"][string], v["title"], v["content"]])
    # 使用词频对列表进行排序
    list_search_result.sort(key=lambda x: x[1], reverse=True)


if __name__ == "__main__":

    list_URL_sport=['https://imgurl.org/']
    list_URL_sport=crawl(list_URL_sport)
    print(list_URL_sport)

    time_start_crawler = time.time()
    crawler(list_URL_sport)
    print(dict_result)
    time_end_crawler = time.time()
    print("网页爬取和分析时间：", time_end_crawler - time_start_crawler)

    word = input("请输入查询的关键词：")
    time_start_search = time.time()
    search(word)
    time_end_search = time.time()
    print("检索时间：", time_end_search - time_start_search)

    for i, row in enumerate(list_search_result): 
        print(i+1, "标题：", row[2])
        print("  网址：",row[0])
        print("  词频：",row[1])
        print("  摘要：",row[3])

# dict_result格式：{"1":
#                       {"url": "xxxxx", "word": {"word1": x, "word2": x, "word3": x}, "title": "中文"}
#                  "2":
#                       {"url": "xxxxx", "word": {"word1": x, "word2": x, "word3": x}, "title": "中文"}
#                 }