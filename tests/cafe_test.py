# -*- coding: utf8 -*-

import unittest
from nose import tools as nt
import mock

import urlparse
from datetime import datetime, date
#import urllib2

from xyz.daum.cafe import Cafe, Board, Article, parse_comments_from_article_album_view
from utils import *



#_originals = {}
#def mock(module, method_name, function=None):
#    _originals[(module, method_name)] = getattr(module, method_name)
#    setattr(getattr(module, method_name), function)
#    return function
#
#
#def restore():
#    for module, method_name in _originals.items():
#        setattr(module, method_name)
#
#import socket

#class FakeResponse:
#    def __init__(self, html, status=200, **kwargs):
#        self.dict = kwargs
#        self.__html = html
#        self.status = status
#        self.headers = {}
#    def read(self):
#        return self.__html
loveclimb_html = open('tests/mock/loveclimb.html').read()
maininner_html = open('tests/mock/home_grpid_ccJT.html').read()
bbsmenu_html   = open('tests/mock/bbs_menu_ajax_ccJT.html').read().decode('utf8')

boardclubalbum_html   = open('tests/mock/board_clubalbum.html').read().decode('euckr')
boardwelcome_html     = open('tests/mock/board_welcome.html').read().decode('euckr')
boardrecent_html      = open('tests/mock/board_recent.html').read().decode('euckr')
boardoneline_html     = open('tests/mock/board_oneline.html').read().decode('euckr')
boardalbum_html       = open('tests/mock/board_album.html').read().decode('euckr')
articleclubalbum_html = open('tests/mock/article_clubalbum.html').read().decode('euckr')
articlewelcome_html   = open('tests/mock/article_welcome.html').read().decode('euckr')
deleted_comment_html  = open('tests/mock/article_deleted_comment.html').read().decode('euckr')

CLUBALBUM_BOARD_URL   = 'http://cafe986.daum.net/_c21_/album_list?grpid=ccJT&fldid=_album'
CLUBALBUM_ARTICLE_URL = 'http://cafe986.daum.net/_c21_/album_read?grpid=ccJT&fldid=_album&page=1&prev_page=0&firstbbsdepth=&lastbbsdepth=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz&contentval=001EWzzzzzzzzzzzzzzzzzzzzzzzzz&datanum=4744&edge=&listnum=15'
WELCOME_BOARD_URL   = 'http://cafe986.daum.net/_c21_/bbs_list?grpid=ccJT&fldid=9urS'
WELCOME_ARTICLE_URL = 'http://cafe986.daum.net/_c21_/bbs_read?grpid=ccJT&mgrpid=&fldid=9urS&page=1&prev_page=0&firstbbsdepth=&lastbbsdepth=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz&contentval=0013ozzzzzzzzzzzzzzzzzzzzzzzzz&datanum=4080&listnum=20'
RECENT_BOARD_URL    = 'http://cafe986.daum.net/_c21_/recent_bbs_list?grpid=ccJT&fldid=_rec'
ONELINE_BOARD_URL   = 'http://cafe986.daum.net/_c21_/memo_list?grpid=ccJT&fldid=_memo'
ALBUM_BOARD_URL     = 'http://cafe986.daum.net/_c21_/album_list?grpid=ccJT&fldid=6bUe'
PIE_BOARD_URL       = 'http://cafe986.daum.net/_c21_/pie?grpid=ccJT&fldid=_pie'

def urlread_side_effect(*args, **kwargs):
    url = args[0]
    if url == 'http://cafe.daum.net/loveclimb':
        return loveclimb_html
    elif url == 'http://cafe986.daum.net/_c21_/home?grpid=ccJT':
        return maininner_html
    elif url.startswith('http://cafe986.daum.net/_c21_/bbs_menu_ajax?grpid=ccJT'):
        return bbsmenu_html
    elif url == CLUBALBUM_BOARD_URL:   return boardclubalbum_html
    elif url == CLUBALBUM_ARTICLE_URL: return articleclubalbum_html
    elif url == WELCOME_BOARD_URL:     return boardwelcome_html
    elif url == WELCOME_ARTICLE_URL:   return articlewelcome_html
    elif url == RECENT_BOARD_URL:      return boardrecent_html
    elif url == ONELINE_BOARD_URL:     return boardoneline_html
    elif url == ALBUM_BOARD_URL:       return boardalbum_html


class CafeTestCase(unittest.TestCase):
    def test_receives_domain_as_argument(self):
        cafe = Cafe('loveclimb')
        nt.eq_(cafe.domain, 'loveclimb')

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_boards_returns_objects_with_name(self, urlread_):
        cafe = Cafe('loveclimb')
        for b in cafe.boards:
            b.name

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_first_call_to_boards_calls_http_request(self, urlread_):
        '''
            calls: cafe.url
            calls: cafe.inner_url
            calls: cafe.sidebar_url
        '''
        Cafe('loveclimb').boards

        # url and inner_url
        urlread_.assert_has_calls([
            mock.call('http://cafe.daum.net/loveclimb', timeouts=mock.ANY),
            mock.call('http://cafe986.daum.net/_c21_/home?grpid=ccJT', timeouts=mock.ANY),
        ])

        call3 = urlread_.call_args_list[2]
        called_url = urlparse.urlparse(call3[0][0])
        # match sidebar_url
        nt.eq_(called_url.hostname + called_url.path, 'cafe986.daum.net/_c21_/bbs_menu_ajax')
        query_dict = querydecode(called_url.query)
        nt.assert_true(include_dict(query_dict, querydecode('grpid=ccJT') ))


    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_get_board_names(self, urlread_):
        BOARD_NAMES = [
            u'최신글 보기', u'더탑 소개', u'클라이밍 전과 후 무엇이 달라졌을까?', u'가입인사. 등업신청', u'이런말 저런말', u'한 줄 메모장', u'오늘은 무슨일이?(회원소식)', u'산모임더탑 소식', u'등반 기록', u'THE TOP 등반교실', u'THE TOP 암.빙벽반 수료', u'단체강습일정', u'등반/산행계획', u'등반/산행후기', u'클럽앨범', u'산 속 프라이팬', u'클라이밍 정보', u'클라이밍동영상', u'건강.다이어트 정보', u'스팸 신고', u'Squamish', u'Bugaboo', u'Skaha', u'안나푸르나', u'파타고니아', u'리우데자네이루', u'크라비', u'2012크라비 등반', u'Q&A질의란', u'지식인에게 물어봐 주세요', u'대기! [잠시 쉼]', u'카페파이', u'인기글 보기', u'이미지 보기', u'동영상 보기', u'투표', ]
        #
        cafe = Cafe('loveclimb')
        board_names = sorted(b.name for b in cafe.boards)
        nt.eq_(board_names, sorted(BOARD_NAMES))


    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_calling_board_runs_only_once(self, urlread_):
        # call boards twice
        cafe = Cafe('loveclimb')
        [b.name for b in cafe.boards]
        [b.name for b in cafe.boards]

        # call to cafe.url should only be called once
        called_urls = [c[0][0] for c in urlread_.call_args_list]
        nt.eq_(called_urls.count(cafe.url), 1)

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_get_single_board(self, urlread_):
        cafe = Cafe('loveclimb')

        # url
        board = cafe.find_board(url=CLUBALBUM_BOARD_URL)
        nt.eq_(board.url, CLUBALBUM_BOARD_URL)

        # name
        board = cafe.find_board(name=u"클럽앨범")
        nt.eq_(board.name, u"클럽앨범")

        # url and name
        board = cafe.find_board(url=CLUBALBUM_BOARD_URL, name=u"클럽앨범")
        nt.eq_(board.name, u"클럽앨범")
        nt.eq_(board.url, CLUBALBUM_BOARD_URL)

        # lambda
        board = cafe.find_board(lambda b: b.name == u"클럽앨범")
        nt.eq_(board.name, u"클럽앨범")

        # None if none
        board = cafe.find_board(name=u"NO SUCH BOARD NAME")
        nt.assert_is_none(board)

        # error if more than one
        with nt.assert_raises(Exception):
            board = cafe.find_board(lambda b: True)


class CafeBoardsTestCase(unittest.TestCase):
    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_called_boards_should_have_url(self, urlread_):
        cafe = Cafe('loveclimb')
        board = [b for b in cafe.boards if b.name == u'클럽앨범'][0]
        #
        nt.eq_(board.url, CLUBALBUM_BOARD_URL)

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_called_boards_should_have_grpid_and_fldid(self, urlread_):
        cafe = Cafe('loveclimb')
        board = [b for b in cafe.boards if b.name == u'클럽앨범'][0]

        nt.eq_(board.grpid, 'ccJT')
        nt.eq_(board.fldid, '_album')

    #@mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    #def test_called_baords_should_have_list_of_articles(self, urlread_):
    #    cafe = Cafe('loveclimb')
    #    board = [b for b in cafe.boards if b.name == u'클럽앨범'][0]
    #    nt.assert_true(len(board.articles) >= 0)

class BoardTestCase(unittest.TestCase):
    def test_should_have_url(self):
        # only url: ok
        Board(url=CLUBALBUM_BOARD_URL)

        # only name: not ok
        with nt.assert_raises(Exception):
            Board(name='u클럽앨범')

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_should_have_grpid_and_fldid(self, urlread_):
        board = Board(url=CLUBALBUM_BOARD_URL, category='icon_phone')

        nt.eq_((board.grpid, board.fldid), ('ccJT', '_album'))



class BoardArticlesTestCase(unittest.TestCase):
    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_first_call_to_articles_calls_http_request(self, urlread_):
        '''First call on board.articles should open: board.url '''
        Board(url=CLUBALBUM_BOARD_URL).articles

        # assert url called
        urlread_.assert_called_once_with(
            CLUBALBUM_BOARD_URL, timeouts=mock.ANY)

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_calling_articles_runs_only_once(self, urlread_):
        # call boards twice
        board = Board(url=CLUBALBUM_BOARD_URL)
        board.articles
        board.articles

        # call to cafe.url should only be called once
        called_urls = [c[0][0] for c in urlread_.call_args_list]
        nt.eq_(called_urls.count(board.url), 1)

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_called_articles_should_have_url(self, urlread_):
        board = Cafe('loveclimb').board(url=CLUBALBUM_BOARD_URL)
        article = [a for a in board.articles if a.title.startswith(u'0704 이대')][0]
        nt.eq_(article.url, CLUBALBUM_ARTICLE_URL)

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_called_articles_should_have_grpid_and_fldid(self, urlread_):
        board = Cafe('loveclimb').board(url=CLUBALBUM_BOARD_URL)
        article = [a for a in board.articles if a.title.startswith(u'0704 이대')][0]

        nt.eq_(article.grpid, 'ccJT')
        nt.eq_(article.fldid, '_album')

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_should_have_parent_board(self, urlread_):
        board = Cafe('loveclimb').board(url=CLUBALBUM_BOARD_URL)
        article = [a for a in board.articles if a.title.startswith(u'0704 이대')][0]

        nt.eq_(article.board, board)

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_should_parse_welcome_board_correctly(self, urlread_):
        # welcome board
        board = Cafe('loveclimb').board(url=WELCOME_BOARD_URL)
        article = board.articles[6]
        nt.eq_(article.url, 'http://cafe986.daum.net/_c21_/bbs_read?grpid=ccJT&mgrpid=&fldid=9urS&page=1&prev_page=0&firstbbsdepth=&lastbbsdepth=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz&contentval=0013wzzzzzzzzzzzzzzzzzzzzzzzzz&datanum=4088&listnum=20')

        # recent board
        board = Cafe('loveclimb').board(url=RECENT_BOARD_URL)
        article = board.articles[3]
        nt.eq_(article.url, 'http://cafe986.daum.net/_c21_/recent_bbs_read?grpid=ccJT&fldid=_album&page=1&prev_page=0&contentval=001Eazzzzzzzzzzzzzzzzzzzzzzzzz&datanum=4748&regdt=20120708230149&listnum=20')

        # oneline board
        board = Cafe('loveclimb').board(url=ONELINE_BOARD_URL)
        nt.eq_(len(board.articles), 20)
        article = board.articles[1]
        nt.eq_(article.url, None)
        nt.eq_(article.nickname, u"Ellen[이경민]")
        nt.eq_(article.content,  u"7/15(일) 오후 2시에 강서구 등촌동 저희집에서 집들이 할께요! \n참석 가능하시면 댓글 달아주세요~ ㅎㅎ좀 멀긴하지만 맛있는 음식과 술이 기다리고 있을거예요~ ^^")
        nt.eq_(article.title,  article.content)
        nt.eq_(article.date, datetime(2012, 7, 11, 9, 45))

        # album board
        board = Cafe('loveclimb').board(url=ALBUM_BOARD_URL)
        article = board.articles[4]
        nt.eq_(article.url, 'http://cafe986.daum.net/_c21_/album_read?grpid=ccJT&fldid=6bUe&page=1&prev_page=0&firstbbsdepth=&lastbbsdepth=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz&contentval=0000Azzzzzzzzzzzzzzzzzzzzzzzzz&datanum=10&edge=&listnum=15')
        nt.eq_(article.title, u"유석재")

    ## TODO
    #def test_should_set_number_of_articles_to_fetch_per_page(self):
    #    pass


class ArticleTestCase(unittest.TestCase):
    def test_should_have_url(self):
        # only url: ok
        Article(url=CLUBALBUM_ARTICLE_URL)

        # only name: not ok
        with nt.assert_raises(Exception):
            Article(title=u'0704 이대')

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_date_should_return_either_datetime_or_date(self, urlread_):
        # datetime
        a = Article(url=CLUBALBUM_ARTICLE_URL, date=u'12.08.14. 10:31')
        nt.eq_(a.date, datetime(2012,8,14, 10,31))

        # date
        a = Article(url=CLUBALBUM_ARTICLE_URL, date=u'12.08.13')
        nt.eq_(a.date, date(2012, 8, 13))

        # today's datetime
        today = datetime.today()
        a = Article(url=CLUBALBUM_ARTICLE_URL, date=u'08:02')
        nt.eq_(a.date, datetime(today.year,today.month,today.day, 8,2))

    def test_is_equal_if_url_is_same(self):
        a1 = Article(url='abc')
        a2 = Article(url='abc')
        a3 = Article(url='def')

        nt.ok_(a1 == a2)
        nt.eq_(a1 == a3, False)


class ArticleCommentsTestCase(unittest.TestCase):
    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_first_call_to_comments_calls_http_request(self, urlread_):
        '''First call on article.comments should open: article.url '''
        Article(url=CLUBALBUM_ARTICLE_URL).comments

        # assert url called
        urlread_.assert_has_calls([
            mock.call(CLUBALBUM_ARTICLE_URL, timeouts=mock.ANY),
        ])

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_calling_comments_runs_only_once(self, urlread_):
        # call boards twice
        article = Article(url=CLUBALBUM_ARTICLE_URL)
        article.comments
        article.comments

        # call to cafe.url should only be called once
        called_urls = [c[0][0] for c in urlread_.call_args_list]
        nt.eq_(called_urls.count(article.url), 1)

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_called_comments_should_have_nickname_date_and_content(self, urlread_):
        article = Article(url=CLUBALBUM_ARTICLE_URL)

        # has comments
        nt.eq_(len(article.comments), 7)

        # parses correctly
        comment = [c for c in article.comments][0]
        nt.eq_(comment.nickname, u'강혜경')
        nt.eq_(comment.date, datetime(2012, 7, 5, 10, 21)) # 12.07.05 10:21
        nt.eq_(comment.content, u'아애들 너무 이쁘네요~~~쌤하고 종신선배 너무 좋으셨겠어요!')

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_should_parse_multiple_line_comments(self, urlread_):
        html = articleclubalbum_html.replace(
            u'아애들 너무 이쁘네요~~~쌤하고 종신선배 너무 좋으셨겠어요!', 
            u'아애들<br>너무 이쁘네요~~~')
        comments = parse_comments_from_article_album_view(url=CLUBALBUM_ARTICLE_URL, text=html)

        # parses correctly
        comment = comments[0]
        nt.eq_(comment.content, u'아애들\n너무 이쁘네요~~~')

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_should_parse_welcome_board_correctly(self, urlread_):
        article = Article(url=WELCOME_ARTICLE_URL)

        # has comments
        nt.eq_(len(article.comments), 2)

        # parses correctly
        comment = [c for c in article.comments][0]
        nt.eq_(comment.nickname, u'도초강(강세원)')
        nt.eq_(comment.date, datetime(2012, 7, 7, 23, 24))
        nt.eq_(comment.content, u'현재 주말반은 마감이 된 상태이구요. 8월반은 7월 23일 저녂쯤  모집 공지 올라갑니다. 토, 일 이틀간 수업을 다 들으실 분만 가능합니다. 이틀 중 하루만 듣는다고해서 가격적 혜택을 드리진 않습니다. ^^')

    @mock.patch('xyz.daum.cafe.urlread', side_effect=lambda *args, **kwargs: deleted_comment_html)
    def test_should_ignore_deleted_comment(self, urlread_):
        article = Article(url=WELCOME_ARTICLE_URL)

        nt.eq_(len(article.comments), 1)


#class CommentsTestCase(unittest.TestCase):
#    def test_parsing_comments




if __name__ == '__main__':
    unittest.main()

