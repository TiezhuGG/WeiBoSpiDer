# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import *

class WeiboSpiderSpider(scrapy.Spider):
    name = 'weibo_spider'
    allowed_domains = ['m.weibo.cn']
    # 用户详情API
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&containerid=100505{uid}'
    # 关注列表API
    follows_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    # 粉丝列表API
    fans_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&since_id={page}'
    # 微博API
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&containerid=107603{uid}&page={page}'
    # 选取一个大V的微博ID作请求起点
    start_uids = ['1822796164']

    def start_requests(self):
        for uid in self.start_uids:
            yield scrapy.Request(self.user_url.format(uid=uid), callback=self.parse_user)

    def parse_user(self, response):
        '''
        解析用户信息
        :param response: Response对象
        '''
        result = json.loads(response.text)
        if result.get('data').get('userInfo'):
            user_info = result.get('data').get('userInfo')
            user_item = UserItem()
            field_map = {
                'id': 'id', 'name': 'screen_name', 'avatar': 'profile_image_url', 'cover': 'cover_image_phone',
                'gender': 'gender', 'description': 'description', 'fans_count': 'followers_count',
                'follows_count': 'follow_count', 'weibos_count': 'statuses_count', 'verified': 'verified',
                'verified_reason': 'verified_reason', 'verified_type': 'verified_type'
            }
            for field, attr in field_map.items():
                user_item[field] = user_info.get(attr)
            yield user_item
            uid = user_info.get('id')
            # 关注
            yield scrapy.Request(self.follows_url.format(uid=uid,page=1), callback=self.parse_follows, meta={'uid':uid, 'page':1})
            # 粉丝
            yield scrapy.Request(self.fans_url.format(uid=uid,page=1), callback=self.parse_fans, meta={'uid':uid, 'page':1})
            # 微博
            yield scrapy.Request(self.weibo_url.format(uid=uid,page=1), callback=self.parse_weibo, meta={'uid':uid, 'page':1})

    def parse_follows(self, response):
        '''
        解析用户关注
        :param response: Response对象
        '''
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) \
            and result.get('data').get('cards')[-1].get('card_group'):
            # 解析每个关注用户信息
            follows = result.get('data').get('cards')[-1].get('card_group')
            for follow in follows:
                if follow.get('user'):
                    uid = follow.get('user').get('id')
                    yield scrapy.Request(self.user_url.format(uid=uid), callback=self.parse_user)

            # 该用户关注列表
            uid = response.meta.get('uid')
            user_relation_item = UserRelationItem()
            follows = [{'id': follow.get('user').get('id'), 'name': follow.get('user').get('screen_name')}
                       for follow in follows]
            user_relation_item['id'] = uid
            user_relation_item['follows'] = follows
            user_relation_item['fans'] = []
            yield user_relation_item
            # 下一页关注
            page = response.meta.get('page') + 1
            yield scrapy.Request(self.follows_url.format(uid=uid, page=page), callback=self.parse_follows,
                                 meta={'uid':uid, 'page':page})

    def parse_fans(self, response):
        '''
        解析用户粉丝
        :param response: Response对象
        '''
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) \
                and result.get('data').get('cards')[-1].get('card_group'):
            # 解析每个粉丝用户信息
            fans = result.get('data').get('cards')[-1].get('card_group')
            for fan in fans:
                if fan.get('user'):
                    uid = fan.get('user').get('id')
                    yield scrapy.Request(self.user_url.format(uid=uid), callback=self.parse_user)

            # 该用户粉丝列表
            uid = response.meta.get('uid')
            user_relation_item = UserRelationItem()
            follows = [{'id': fan.get('user').get('id'), 'name': fan.get('user').get('screen_name')}
                       for fan in fans]
            user_relation_item['id'] = uid
            user_relation_item['fans'] = fans
            user_relation_item['follows'] = []
            yield user_relation_item
            # 下一页粉丝
            page = response.meta.get('page') + 1
            yield scrapy.Request(self.fans_url.format(uid=uid, page=page), callback=self.parse_fans,
                                 meta={'uid': uid, 'page': page})

    def parse_weibo(self, response):
        '''
        解析微博列表
        :param response: Response对象
        '''
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards'):
            weibos = result.get('data').get('cards')
            for weibo in weibos:
                mblog = weibo.get('mblog')
                if mblog:
                    weibo_item = WeiboItem()
                    field_map = {
                        'id': 'id', 'attitudes_count': 'attitudes_count', 'comments_count': 'comments_count',
                        'reposts_count': 'reposts_count', 'picture': 'original_pic', 'pictures': 'pics',
                        'created_at': 'created_at', 'source': 'source', 'text': 'text', 'raw_text': 'raw_text',
                        'thumbnail': 'thumbnail_pic',
                    }
                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                    weibo_item['user'] = response.meta.get('uid')
                    yield weibo_item

            # 下一页微博
            uid = response.meta.get('uid')
            page = response.meta.get('page') + 1
            yield scrapy.Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibo,
                                 meta={'uid':uid, 'page':page})