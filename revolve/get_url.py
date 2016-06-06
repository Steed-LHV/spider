#!/usr/bin/env python
#coding=utf-8

import requests, time, json
from bs4 import BeautifulSoup
from aladin.helpers import toint
from db_conn import CollectionQueue, CollectionHistory, session, headers, Goods
import re
import httplib
httplib._MAXHEADERS = 1000
s = requests.session()


class GetRevolve():
    def __init__(self, url, category='', secondary_category=''):
        self.url = url
        self.pages_list = []
        self.site_name = 'Revolve'
        self.category = category
        self.second_category = secondary_category
        self.check_page()
        self.start_page()

    def requests_page(self, url, retry=0, max_retry=3):
        # print url
        if retry > max_retry:
            return None

        try:
            r = s.get(url, headers=headers, timeout=60)
            if r:
                print r
            else:
                print '============'
            if r.status_code != 200:
                raise Exception("[Status Code Error] %s" % r.status_code)
            return r.text
        except Exception, e:
            print Exception
            print e
            print("[Requests Page Error] url:%s" % url)
            time.sleep(retry + 1)
            return self.requests_page(url, retry=retry + 1)

    def check_page(self):
        html_text = self.requests_page(self.url)
        if not html_text:
            return
        soup = BeautifulSoup(html_text)
        page_number = soup.find(attrs={"class":"plp_pagination_wrap"}).findAll("li")[-1].text
        print page_number
        page_number = toint(page_number) + 1

        page_list = soup.find(attrs={"rel":"canonical"}).attrs.get('href')
        # print page_list
        for i in range(1,page_number):
            url = page_list + '?&pageNum=%s' %i
            print url
            self.pages_list.append(url)

    def start_page(self):
        for index, page in enumerate(self.pages_list):
            self.get_page(page, index + 1)

    def get_page(self, url, page_number):
        # print url
        html_text = self.requests_page(url)
        if not html_text:
            return
        soup = BeautifulSoup(html_text)
        product_list = soup.select("li.item")
        for index , p in enumerate(product_list):
            rank = (page_number - 1) * 96 + index + 1
            # print rank
            # print index
            # print p
            # data_url = p.select()
            # print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
            data_url = p.select("a.plp_text_link")[0].attrs.get('href')
            true_data_url = 'http://www.revolve.com/'+data_url
            print true_data_url

            find_queue = session.query(CollectionQueue).filter(CollectionQueue.site_name == 'Revolve') \
                .filter(CollectionQueue.url == true_data_url).first()
            print find_queue
            if not find_queue:
                cq = CollectionQueue()
                cq.site_name = self.site_name
                cq.add_time = int(time.time())
                cq.category = self.category
                cq.secondary_category = self.second_category
                cq.rank = rank
                cq.url = true_data_url
                # cq.img_url = img_url
                session.add(cq)
                session.commit()
                print("added....")






# url1 = 'http://www.revolve.com/dresses/br/a8e981/?navsrc=subclothing'
url1 = 'http://www.revolve.com/dresses/br/a8e981/?navsrc=subclothing'
url2 = 'http://www.revolve.com/jackets-coats/br/e4012a/?navsrc=subclothing'
url3 = 'http://www.revolve.com/activewear/br/fcda16/?navsrc=subclothing'
url4 = 'http://www.revolve.com/denim/br/2664ce/?navsrc=subclothing'
url5 = 'http://www.revolve.com/rompers/br/7b019d/?navsrc=subclothing'
url6 = 'http://www.revolve.com/jumpsuits/br/8e3089/?navsrc=subclothing'
url7 = 'http://www.revolve.com/sweaters-knits/br/a49835/?navsrc=subclothing'
url8 = 'http://www.revolve.com/intimates/br/dad0f5/?navsrc=subclothing'
url9 = 'http://www.revolve.com/tops-blouses/br/d01fe8/?navsrc=left'
url10 = 'http://www.revolve.com/tops-tees/br/1e8535/?navsrc=left'
url11 = 'http://www.revolve.com/tops-tanks/br/d3ad99/?navsrc=left'
url12 = 'http://www.revolve.com/tops-bodysuits/br/68e631/?navsrc=left'
url13 = 'http://www.revolve.com/shorts/br/9d2482/?navsrc=subclothing'
url14 = 'http://www.revolve.com/skirts/br/8b6a66/?navsrc=subclothing'
url15 = 'http://www.revolve.com/loungewear/br/97c04e/?navsrc=subclothing'
url16 = 'http://www.revolve.com/swimwear/br/6bd2e6/?navsrc=subclothing'
url17 = 'http://www.revolve.com/pants/br/44d522/?navsrc=subclothing'
url18 = 'http://www.revolve.com/shoes/br/3f40a9/?navsrc=main'
url19 = 'http://www.revolve.com/bags/br/2df9df/?navsrc=main'
url20 = 'http://www.revolve.com/jewelry-accessories-belts/br/ea8542/?navsrc=subaccessories'
url21 = 'http://www.revolve.com/jewelry-accessories-sunglasses-eyewear/br/4c27de/?navsrc=subaccessories'
url22 = 'http://www.revolve.com/jewelry-accessories-gloves/br/6ddfca/?navsrc=subaccessories'
url23 = 'http://www.revolve.com/jewelry-accessories-hats-hair-accessories/br/dcfd6d/?navsrc=subaccessories'
url24 = 'http://www.revolve.com/jewelry-accessories-scarves/br/b95ee6/?navsrc=subaccessories'
url25 = 'http://www.revolve.com/jewelry-accessories-beauty/br/49fd78/?navsrc=subaccessories'
url26 = 'http://www.revolve.com/jewelry-accessories-hosiery-socks/br/c5ef6b/?navsrc=subaccessories'
url27 = 'http://www.revolve.com/jewelry-accessories-jewelry/br/c7e3a4/?navsrc=subaccessories'

if __name__ == '__main__':
    g1 = GetRevolve(url1, 'Women_Apparel', 'Dresses')
    g2 = GetRevolve(url2, 'Women_Apparel', 'Coats')
    g3 = GetRevolve(url3, 'Women_Apparel', 'Fitness & Activewear')
    g4 = GetRevolve(url4, 'Women_Apparel', 'Jeans')
    g5 = GetRevolve(url5, 'Women_Apparel', 'Jumpsuits')
    g6 = GetRevolve(url6, 'Women_Apparel', 'Jumpsuits')
    g7 = GetRevolve(url7, 'Women_Apparel', 'Sweater')
    g8 = GetRevolve(url8, 'Women_Apparel', 'Lingerie')
    g9 = GetRevolve(url9, 'Women_Apparel', 'Blouses')
    g10 = GetRevolve(url10, 'Women_Apparel', 'T-shirts')
    g11 = GetRevolve(url11, 'Women_Apparel', 'Tops')
    g12 = GetRevolve(url12, 'Women_Apparel', 'bodysuit')
    g13 = GetRevolve(url13, 'Women_Apparel', 'Shorts')
    g14 = GetRevolve(url14, 'Women_Apparel', 'Skirts')
    g15 = GetRevolve(url15, 'Women_Apparel', 'Sleepwear')
    g16 = GetRevolve(url16, 'Women_Apparel', 'Swimwear')
    g17 = GetRevolve(url17, 'Women_Apparel', 'Pants')
    g18 = GetRevolve(url18, 'Shoes')
    g19 = GetRevolve(url19, 'Accessories', 'Bags')
    g20 = GetRevolve(url20, 'Accessories', 'Belts')
    g21 = GetRevolve(url21, 'Accessories', 'Sunglasses')
    g22 = GetRevolve(url22, 'Accessories', 'Gloves')
    g23 = GetRevolve(url23, 'Accessories', 'Hats')
    g24 = GetRevolve(url24, 'Accessories', 'Scarves')
    g25 = GetRevolve(url25, 'Accessories', 'Beauty')
    g26 = GetRevolve(url26, 'Accessories', 'Socks')
    g27 = GetRevolve(url27, 'Jewellery')