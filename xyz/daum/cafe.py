#!/usr/bin/python
# -*- coding: utf8 -*-

from collections import namedtuple
from datetime import datetime
import urllib
import urlparse

import lxml.html

from util import *


def parse_cafe_inner_url_from_official(url):
    '''Parse cafe official url and return real url.
    
	<frame name="down" id="down" src="http://cafe986.daum.net/_c21_/home?grpid=ccJT" width="100%" height="100%" frameborder="0" marginwidth="0" marginheight="0" title="카페 메인 프레임">
    '''
    #CAFE_HOME_PATTERN = re.compile(u'''
    #    # get src of frame#down
    #    <frame [^>]*
    #        (
    #            (id="down" [^>]*src="([^"]*)")
    #            |
    #            (src="([^"]*)" [^>]*id="down")
    #        )
    #    [^>]*>
    #''', re.S | re.X)

    site1 = urlread(url, timeouts=ARTICLE_TIMEOUTS)

    #match = CAFE_HOME_PATTERN.search(site1)
    #if not match:
    #    raise Exception("parse error")
    #url = match.group(3) or match.group(5)
    html = lxml.html.fromstring(site1)
    frame = html.cssselect('frame#down')[0]
    url = frame.get('src')

    return url

def parse_sidebar_menu_url_from_cafe_main(url):
    ''' parse cafe main source and return url for cafe sidebar menu '''
    #CAFE_SIDEBAR_PATTERN = re.compile(u'''
    #    <iframe 
    #        [^>]*
    #        id="leftmenu" 
    #        [^>]*
    #        src="([^"]*)"
    #        [^>]*
    #    >
    #''', re.S | re.X)

    text = urlread(url, timeouts=ARTICLE_TIMEOUTS)
    #match = CAFE_SIDEBAR_PATTERN.search(text)
    #if not match:
    #    raise Exception("parse error")

    #path = match.group(1)

    html = lxml.html.fromstring(text)
    frame = html.xpath('//iframe[@id="leftmenu"]')[0] # cssselect didn't work.
    path = frame.get('src')

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
    _type = namedtuple('BoardInfo', 'category id path title content url fldid grpid'.split())

    text = urlread(url, timeouts=ARTICLE_TIMEOUTS)

    html = lxml.html.fromstring(text)
    boards = html.xpath('//li[starts-with(@class, "icon_")]')
    boards = [(b,b.xpath('a')[0]) for b in boards]

    def parse(li, a):
        path = unescape(a.get('href'))
        query_dict = urlparse.parse_qs(urllib.splitquery(path)[-1])
        return _type(
            li.get('class'),
            a.get('id'),
            path,
            unescape(a.get('title')),
            a.text,
            get_domain(url, path),
            query_dict.get('fldid', [None])[0],
            query_dict.get('grpid', [None])[0],
        )

    return [parse(li,a) for (li,a) in boards]


def parse_article_album_list(url, text=None):
    ''' parse article phone list and result list of article information as a tuple:
        (article_num, title, post_date, author, path, url)
    '''
    _type = namedtuple('BriefArticleInfo', 
        'article_num title post_date author path url fldid grpid'.split())

    # fetch
    if text is None:
        text = urlread(url, timeouts=ARTICLE_TIMEOUTS)


    html = lxml.html.fromstring(text)
    articles = html.cssselect('div.albumListBox li')

    def _parse(li):
        subject = li.cssselect('dd.subject a')[0]
        author  = li.cssselect('dd.nick a')[0]
        article_num, post_date = li.cssselect('dd.txt_sub.p11 span.num')
        href = subject.get('href')
        path = unescape(href)
        query_dict = urlparse.parse_qs(urllib.splitquery(path)[-1])
        return _type(
            int(article_num.text.strip()), 
            subject.text.strip(),
            post_date.text.strip(),
            author.text.strip(),
            href,
            get_domain(url, href),
            query_dict.get('fldid', [None])[0],
            query_dict.get('grpid', [None])[0],
        )

    return [_parse(li) for li in articles if not li.cssselect('div.blank_thumb')]


def parse_article_recent_list(url, text=None):
    '''
    <tr>
        <td class="num" nowrap="nowrap">4088</td>
        <td class="headcate txt_sub" nowrap="nowrap">
        </td>
        <td class="subject">
            <a href="/_c21_/bbs_read?grpid=ccJT&mgrpid=&fldid=9urS&page=1&prev_page=0&firstbbsdepth=&lastbbsdepth=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz&contentval=0013wzzzzzzzzzzzzzzzzzzzzzzzzz&datanum=4088&listnum=20">안녕하세요~</a>
            <img src="http://i1.daumcdn.net/cafeimg/cf_img2/img_blank2.gif" width="8" height="12" alt="새글" class="icon_new" />								
        </td>
        <td class="nick">
            <a href="javascript:;"  onclick="showSideView(this, 'A.BbQds8kns0', '', '\uBC15\uC120\uC601'); return false;">박선영</a>
        </td>
        <td class="date" nowrap="nowrap">12.07.08</td>
        <td class="count" nowrap="nowrap">0</td>
        <td class="recommend_cnt" nowrap="nowrap">0</td>
    </tr>
    '''
    _type = namedtuple('BriefArticleInfo', 
        'article_num title post_date author path url'.split())

    # fetch
    if text is None:
        text = urlread(url, timeouts=ARTICLE_TIMEOUTS)
    html = lxml.html.fromstring(text)

    results = []
    articles = html.cssselect('table.bbsList tbody tr')
    for tr in articles:
        subject = tr.cssselect('td.subject a')[0]
        path = subject.get('href')
        nick = tr.cssselect('td.nick a')[0]
        date = tr.cssselect('td.date')[0]
        parsed = urlparse.urlparse(path)
        article_num = urlparse.parse_qs(parsed.query)['datanum'][0]
        results.append(_type(
            int(article_num),
            subject.text_content().strip(),
            date.text.strip(),
            nick.text.strip(),
            path,
            get_domain(url, path),
        ))
    return results

def parse_article_oneline_list(url, text=None):
    '''
    XPATH: //div[@class="memo_list"]/form[@id="listForm"]/ul/dl

    source:
        <dl>
            <dt class="profile_block reply_size" >
            <div id="pimgWrap_0_6475" class="fl">
                <img src="http://fimg.daum-img.net/tenth/img/y/t/i/u/ccJT/76/96c1c9-42087-d1.bmp" width="32" height="32" alt="" onmouseover="MemoFormController.showProfileLayer(this, 'pimg_0_6475');" onmouseout="MemoFormController.hideProfileLayer();">
                <img id="pimg_0_6475" src="http://fimg.daum-img.net/tenth/img/y/t/i/u/ccJT/76/96c1c9-42087-d3.bmp" width="150" height="150" style="display: none;" alt="프로필 이미지" />
            </div>
            </dt>			
            <dd class="content_block ">
            <div id="memoViewer_0_6475" class="content_viewer ">
                <p class="nickname">
                &nbsp; <a href="#" onclick="showSideView(this, 'Zo6UMXQoclc0', '', 'Ellen[\uC774\uACBD\uBBFC]'); return false;" class="b">Ellen[이경민]</a>
                &nbsp; <span class="txt_sub num">12.07.11. 09:45</span> &nbsp;
                </p>
                <div class="content_memo">
                    7/15(일) 오후 2시에 강서구 등촌동 저희집에서 집들이 할께요! 
                    <br />
                    참석 가능하시면 댓글 달아주세요~ ㅎㅎ좀 멀긴하지만 맛있는 음식과 술이 기다리고 있을거예요~ ^^ 
                    <img src="http://i1.daumcdn.net/cafeimg/cf_img2/img_blank2.gif" width="8" height="12" alt="새글" class="icon_new" />
                    <b>								
                        <a href="#" onclick="ReplyFormController.showReplyForm('0_6475'); return false;" class="txt_point" >
                            [<span id="commentReplyCount_0_6475" class="txt_point">8</span>]
                        </a>
                    </b>						
                </div>
            </div><!-- content_viewer -->
            <div id="memoModify_0_6475" class="content_modify"></div>
            <div id="memoBtns_0_6475" class="memo_btns p11">
                <a href="#" onclick="ReplyFormController.showReplyForm('0_6475'); return false;" class="p11">답글</a>																	</div>
            </dd><!-- end content_block -->
        </dl>
    '''
    _type = namedtuple('BriefArticleInfo', 
        'article_num title post_date author path url'.split())

    # fetch
    if text is None:
        text = urlread(url, timeouts=ARTICLE_TIMEOUTS)
    html = lxml.html.fromstring(text)

    results = []
    articles = html.cssselect('div.memo_list form#listForm ul dl')
    for dl in articles:
        content = dl.cssselect('div.content_viewer div.content_memo')[0].xpath('child::text()')
        nick = dl.cssselect('div.content_viewer p.nickname a')[0]
        date = dl.cssselect('div.content_viewer p.nickname span.txt_sub.num')[0]
        article_num = dl.cssselect('div.content_viewer')[0].attrib['id'].rsplit('_', 1)[-1]
        results.append(_type(
            int(article_num),
            "\n".join(content).strip(),
            date.text.strip(),
            nick.text.strip(),
            None,
            None,
        ))
    return results



def parse_article_board_list(url, text=None):
    '''
    <tr>
        <td class="num" nowrap="nowrap">4088</td>
        <td class="headcate txt_sub" nowrap="nowrap">
        </td>
        <td class="subject">
            <a href="/_c21_/bbs_read?grpid=ccJT&mgrpid=&fldid=9urS&page=1&prev_page=0&firstbbsdepth=&lastbbsdepth=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz&contentval=0013wzzzzzzzzzzzzzzzzzzzzzzzzz&datanum=4088&listnum=20">안녕하세요~</a>
            <img src="http://i1.daumcdn.net/cafeimg/cf_img2/img_blank2.gif" width="8" height="12" alt="새글" class="icon_new" />								
        </td>
        <td class="nick">
            <a href="javascript:;"  onclick="showSideView(this, 'A.BbQds8kns0', '', '\uBC15\uC120\uC601'); return false;">박선영</a>
        </td>
        <td class="date" nowrap="nowrap">12.07.08</td>
        <td class="count" nowrap="nowrap">0</td>
        <td class="recommend_cnt" nowrap="nowrap">0</td>
    </tr>
    '''
    _type = namedtuple('BriefArticleInfo', 
        'article_num title post_date author path url'.split())

    # fetch
    if text is None:
        text = urlread(url, timeouts=ARTICLE_TIMEOUTS)
    html = lxml.html.fromstring(text)

    results = []
    articles = html.cssselect('table.bbsList tbody tr')
    for tr in articles:
        subject = tr.cssselect('td.subject a')[0]
        path = subject.get('href')
        nick = tr.cssselect('td.nick a')[0]
        date = tr.cssselect('td.date')[0]
        parsed = urlparse.urlparse(path)
        article_num = urlparse.parse_qs(parsed.query)['datanum'][0]
        results.append(_type(
            int(article_num),
            subject.text_content().strip(),
            date.text.strip(),
            nick.text.strip(),
            path,
            get_domain(url, path),
        ))
    return results



def get_article_num_from_url(url):
    return int(url.rsplit('/', 1)[-1])


def parse_comments_from_article_album_view(url, text=None):
    CSS_SELECTOR = '.commentBox .commentDiv .commentPagingDiv .comment_pos'

    # inner url
    parse_result = urlparse.urlparse(url)
    if parse_result.netloc == 'cafe.daum.net':
        url = parse_cafe_inner_url_from_official(url)

    if text is None:
        text = urlread(url, timeouts=ARTICLE_TIMEOUTS)
    html = lxml.html.fromstring(text)

    comments = html.cssselect(CSS_SELECTOR)
    comments = [Comment(
        nickname=c.cssselect('.id_admin span a')[0].text.strip(),
        content ="\n".join(c.cssselect('.comment_contents')[0].itertext()).strip(),
        date    =c.cssselect('.comment_date')[0].text.strip(),
    ) for c in comments if c.text != u'삭제된 댓글 입니다.']
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

            self.__boards = [Board(name=b.content, url=b.url, category=b.category, fldid=b.fldid, grpid=b.grpid) for b in board_info_list]

        return self.__boards

    def board(self, *args, **kwargs):
        '''find single board matching criteria. '''
        boards = self.boards
        if len(args) == 1 and callable(args[0]):
            boards = [b for b in boards if args[0](b)]
        for key,value in kwargs.items():
            boards = [b for b in boards if getattr(b, key) == value]
        if len(boards) > 1:
            raise Exception("found more than 1 boards")
        if len(boards) == 0:
            return None
        return boards[0]


class Board:
    def __init__(self, url, name=None, category=None, fldid=None, grpid=None):
        self.name = name.strip() if name else name
        self.category = category.strip() if category else category

        self.url = url
        self.__articles = None

        self.__fldid = fldid
        self.__grpid = grpid

    @property
    def fldid(self):
        self.__fldid = self.__fldid  or self.articles[0].fldid
        return self.__fldid

    # TODO: directly parse page, instead of calling articles
    @property
    def grpid(self):
        self.__grpid = self.__grpid or self.articles[0].grpid
        return self.__grpid

    def fetch(self, **options):
        if self.category in ('icon_phone', 'icon_album'):
            articles = parse_article_album_list(self.url)
            articles = [Article(a.url, a.title, a.post_date, a.author, fldid=a.fldid, grpid=a.grpid, board=self) for a in articles]
        elif self.category == 'icon_recent':
            articles = parse_article_recent_list(self.url)
            articles = [Article(a.url, a.title, a.post_date, a.author, board=self) for a in articles]
        elif self.category == 'icon_memo':
            articles = parse_article_oneline_list(self.url)
            articles = [Article(a.url, a.title, a.post_date, a.author, a.title, board=self) for a in articles]
        else:
            articles = parse_article_board_list(self.url)
            articles = [Article(a.url, a.title, a.post_date, a.author, board=self) for a in articles]
        return articles

    def fetch_articles(self, **options):
        return self.fetch(**options)

    @property
    def articles(self):
        if self.__articles is None:
            self.__articles = self.fetch_articles()
        return self.__articles

    def __repr__(self):
        return "<%s>" % self.name.encode('utf8')


class Article:
    def __init__(self, url, title=None, date=None, nickname=None, content=None, fldid=None, grpid=None, board=None):
        self.url = url
        self.title = title
        if self.title is not None:
            self.title = self.title.strip()
        self.content = content
        self.__comments = None
        self.nickname = nickname

        self.raw_date = date
        self.__date = None

        self.fldid = fldid
        self.grpid = grpid
        self.board = board

    def get_date(self):
        '''returns either datetime.datetime if fully fetched, or 
        datetime.datetime instance if not.
        '''
        if self.__date is None or not isinstance(self.__date, datetime):
            self.__date = parse_date(self.raw_date)
        return self.__date
    date = property(get_date)

    @property
    def comments(self):
        if self.__comments is None:
            self.__comments = parse_comments_from_article_album_view(self.url)
        return self.__comments

    def __hash__(self):
        return hash((self.url, self.fldid, self.grpid, self.raw_date, self.title, self.content, self.nickname))

    def __repr__(self):
        return "<%s,%s>" % (self.title.encode('utf8'), self.raw_date.encode('utf8'))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return False


def parse_date(raw_date):
    '''try parsing raw date string, and return either datetime.datetime or datetime.date. '''
    try:
        return datetime.strptime(raw_date, "%y.%m.%d. %H:%M")
    except ValueError:
        try:
            return datetime.strptime(raw_date, "%y.%m.%d").date()
        except ValueError:
            today = datetime.today().date()
            time  = datetime.strptime(raw_date, "%H:%M").time()
            return datetime.combine(today, time)


class Comment:
    def __init__(self, nickname, content, date):
        self.nickname = nickname
        self.content = content
        self.raw_date = date
        self.__date = None

    def get_date(self):
        if self.__date is None or not isinstance(self.__date, datetime):
            self.__date = parse_date(self.raw_date)
        return self.__date
    date = property(get_date)

    def __repr__(self):
        return (u"<%s,%s,%s>" % (self.content, self.nickname, self.raw_date)).encode('utf8')


# vim: sts=4 et
