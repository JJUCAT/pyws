#! /usr/bin/python3
# code: UTF-8

import requests
from bs4 import BeautifulSoup
import os

# 确保这个目录存在，如果不存在则创建
if not os.path.exists('downloaded_images'):
    os.makedirs('downloaded_images')

def download_image(image_url, image_name):
    """下载图片并保存到指定文件夹"""
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(f'downloaded_images/{image_name}', 'wb') as f:
            f.write(response.content)

def crawl_page(url):
    """爬取指定网页的图片"""
    response = requests.get(url)
    if response.status_code == 200:
        print('get url response...')
        # soup = BeautifulSoup(response.text, 'html.parser')
        # # 假设图片都在<img>标签中，并且有一个src属性
        # images = soup.find_all('img')
        # for img in images:
        #     img_url = img.get('src')
        #     # 确保图片链接是完整的URL
        #     if not img_url.startswith('http'):
        #         img_url = url + img_url
        #     # 构造图片名称，这里简单地使用图片URL的最后部分作为文件名
        #     img_name = img_url.split('/')[-1]
        #     download_image(img_url, img_name)

def crawl_and_turn_page(base_url, page_count):
    """爬取指定数量的页面，并翻页"""
    for i in range(1, page_count + 1):
        current_page_url = base_url+str(i)
        print(f"Crawling page {i}...")
        print("url:%s" % (current_page_url))
        crawl_page(current_page_url)

# 用实际的URL替换下面的base_url和page_count
base_url = 'https://e-hentai.org/s/5204830bdf/2930972-'
# base_url = 'https://baijiahao.baidu.com/s?id=1717846450279628377&wfr=spider&for=pc'
page_count = 1

crawl_and_turn_page(base_url, page_count)
