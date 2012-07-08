#!/usr/bin/python
# -*- coding: utf8 -*-

import re
from collections import namedtuple
import lxml.html
from datetime import datetime

from util import *


def parse_cafe_inner_url_from_official(url):
    ''' parse cafe official url and return real url 
    
    '''
    CAFE_HOME_PATTERN = re.compile(u'''
        # get src of frame#down
        <frame [^>]*
            (
                (id="down" [^>]*src="([^"]*)")
                |
                (src="([^"]*)" [^>]*id="down")
            )
        [^>]*>
    ''', re.S | re.X)

    site1 = urlread(url, timeouts=ARTICLE_TIMEOUTS)
    match = CAFE_HOME_PATTERN.search(site1)
    if not match:
        raise Exception("parse error")
    url = match.group(3) or match.group(5)
    return url

def parse_sidebar_menu_url_from_cafe_main(url):
    ''' parse cafe main source and return url for cafe sidebar menu '''
    CAFE_SIDEBAR_PATTERN = re.compile(u'''
        <iframe 
            [^>]*
            id="leftmenu" 
            [^>]*
            src="([^"]*)"
            [^>]*
        >
    ''', re.S | re.X)

    text = urlread(url, timeouts=ARTICLE_TIMEOUTS)
    match = CAFE_SIDEBAR_PATTERN.search(text)
    if not match:
        raise Exception("parse error")

    path = match.group(1)
    sidebar_url = get_domain(url, path)
    return sidebar_url


def parse_board_info_from_sidebar(url):
    ''' parse cafe menu source and return list of menu information in tuple:
        (category, id, path, title, content, url)

    url is cafe sidebar menu url

    some of examples are:
            <li class="icon_movie_all "><a id="fldlink_movie_bbs" href="/_c21_/movie_bbs_list?grpid=ccJT" target="_parent" onclick="parent_().caller(this.href);return false;" title="&#46041;&#50689;&#49345; &#48372;&#44592;">동영상 보기</a></li>
            <li class="icon_board "><a id="fldlink_9VHG_286" href="/_c21_/bbs_list?grpid=ccJT&amp;fldid=9VHG" target="_parent" onclick="parent_().caller(this.href);return false;" class="" title="&#54616;&#44256;&#49910;&#51008;&#47568; &#47924;&#49832;&#47568;&#51060;&#46304; &#54624; &#49688; &#51080;&#45716; &#44277;&#44036;&#51077;&#45768;&#45796;">이런말 저런말</a></li>
            <li class="icon_album "><a id="fldlink_6bUe_338" href="/_c21_/album_list?grpid=ccJT&amp;fldid=6bUe" target="_parent" onclick="parent_().caller(this.href);return false;" title="climbing picture &amp; info.">Squamish</a></li>
            <li class="icon_phone "><a id="fldlink__album_624" href="/_c21_/album_list?grpid=ccJT&amp;fldid=_album" target="_parent" onclick="parent_().caller(this.href);return false;" title="&#53364;&#47101;&#50536;&#48276;">클럽앨범</a></li>
            <li class="icon_memo "><a id="fldlink__memo_525" href="/_c21_/memo_list?grpid=ccJT&amp;fldid=_memo" target="_parent" onclick="parent_().caller(this.href);return false;" title="&#51068;&#49345;&#51032; &#49692;&#44036;&#49692;&#44036; &#46496;&#50724;&#47476;&#45716; &#51105;&#45392;&#51060;&#45208;,&#44036;&#45800;&#54620; &#47700;&#49464;&#51648;&#47484; &#51201;&#50612;&#48372;&#49464;&#50836;!!">한 줄 메모장</a><img src="http://i1.daumcdn.net/cafeimg/cf_img2/img_blank2.gif" width="10" height="9" alt="new" class="icon_new" /></li> 
    '''
    _type = namedtuple('BoardInfo', 'category id path title content url'.split())

    BOARD_PATTERN = re.compile(u'''
        <li [^>]*                               # LI
            class="(?P<category>icon_[^"]*)\s*" # class attribute
        >
            \s*
            <a                                  # A
                [^>]*
                id="(?P<id>[^"]*)"              # id attribute
                [^>]*
                href="(?P<path>[^"]*)"          # href attribute
                [^>]*
                title="(?P<title>[^"]*)"        # title attribute
                [^>]*
            >
                (?P<content>[^<]*)              # text node under A
            </a>
            \s*

            (                                   # optional new-post image
                <img[^?]*>
            )?
            \s*
        </li>
    ''', re.X | re.S)

    text = urlread(url, timeouts=ARTICLE_TIMEOUTS)
    result = BOARD_PATTERN.findall(text)
    return [_type(
        t[0].strip(),                # class
        t[1],                        # id
        unescape(t[2], repeat=True), # href
        unescape(t[3], repeat=True), # title
        t[4],                        # text
        get_domain(url, t[2]),       # domain
    ) for t in result]


def parse_article_album_list(url, text=None):
    ''' parse article album list and result list of article information as a tuple:
        (article_num, title, post_date, author, path, url)
    '''
    _type = namedtuple('BriefArticleInfo', 
        'article_num title post_date author path url'.split())

    ARTICLE_LIST_START_MARK = '''<div class="albumListBox">'''
    ARTICLE_LIST_END_MARK   = '''<!-- end albumListBox -->'''

    # fetch
    if text is None:
        text = urlread(url, timeouts=ARTICLE_TIMEOUTS)

    if not(ARTICLE_LIST_START_MARK in text and ARTICLE_LIST_END_MARK in text):
        raise Exception("parse error")
    text = text[ text.index(ARTICLE_LIST_START_MARK): text.index(ARTICLE_LIST_END_MARK) ]

    ARTICLE_PATTERN = re.compile(u'''
        <li[^>]*>\s*
            <dl>
            .*?
            <dd[ ]class="subject">\s*
                <a[ ][^>]*href="(?P<path>[^"]*)"[^>]*>\s*       # path
                (?P<title>[^<]*)\s*                             # title
                </a>\s*
                .*?
            </dd>\s*
            <dd[ ]class="txt_sub[ ]p11">번호\s*
            <span[ ]class="num">(?P<article_num>[0-9]+)</span>  # article_num
            .*?
            <span[ ]class="num">(?P<post_date>[^<]*)</span>\s*  # post_date
            </dd>
            .*?
            <dd[ ]class="txt_sub[ ]nick[ ]p11">\s*
                <a[^>]*>(?P<author>[^<]*)</a>\s*                # author
            </dd>
            .*?
            </dl>
            .*?
        </li>
    ''', re.X | re.S)

    result = []
    for article in text.split('</li>')[:-1]:
        match = ARTICLE_PATTERN.search(article + '</li>')
        if match:
            # (article_num, title, post_date, author, path)
            d = match.groupdict()
            t = (
                int(d['article_num']), 
                d['title'].strip(), 
                d['post_date'], 
                d['author'].strip(), 
                d['path'],
                get_domain(url, d['path']),
            )
            result.append(_type(*t))

    return result


def get_article_num_from_url(url):
    return int(url.rsplit('/', 1)[-1])


def parse_comments_from_article_album_view(url):
    CSS_SELECTOR = '.commentBox .commentDiv .commentPagingDiv .comment_pos'

    # inner url
    parse_result = urlparse.urlparse(url)
    if parse_result.netloc == 'cafe.daum.net':
        url = parse_cafe_inner_url_from_official(url)

    htmlstring = urlread(url, timeouts=ARTICLE_TIMEOUTS)
    html = lxml.html.fromstring(htmlstring)

    comments = html.cssselect(CSS_SELECTOR)
    comments = [Comment(
        nickname=c.cssselect('.id_admin span a')[0].text.strip(),
        content =c.cssselect('.comment_contents')[0].text.strip(),
        date    =c.cssselect('.comment_date')[0].text.strip(),
    ) for c in comments]
    return comments


class Cafe:
    def __init__(self, domain):
        self.domain = domain
        self.url = 'http://cafe.daum.net/' + self.domain
        self.__boards = None

    @property
    def boards(self):
        if self.__boards is None:
            inner_url       = parse_cafe_inner_url_from_official(self.url)
            sidebar_url     = parse_sidebar_menu_url_from_cafe_main(inner_url)
            board_info_list = parse_board_info_from_sidebar(sidebar_url)
            # (category, id, path, title, content, url)

            self.__boards = [Board(name=b.content, url=b.url) for b in board_info_list]

        return self.__boards


class Board:
    def __init__(self, url, name=None):
        if name:
            self.name = name.strip()

        self.url = url
        self.__articles = None


    @property
    def articles(self):
        if self.__articles is None:
            self.__articles = parse_article_album_list(self.url)
        return self.__articles


class Article:
    def __init__(self, url, title=None):
        self.url = url
        if title:
            self.title = title.strip()
        self.__comments = None

    @property
    def comments(self):
        if self.__comments is None:
            self.__comments = parse_comments_from_article_album_view(self.url)
        return self.__comments


class Comment:
    def __init__(self, nickname, content, date):
        self.nickname = nickname
        self.content = content
        self.raw_date = date
        self.__date = None

    @property
    def date(self):
        '''12.07.05. 10:21'''
        if self.__date is None:
            self.__date = datetime.strptime(self.raw_date, "%y.%m.%d. %H:%M")
        return self.__date




# vim: sts=4 et
