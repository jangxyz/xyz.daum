# -*- coding: utf8 -*-

import unittest
from nose import tools as nt
import mock

import urlparse
from datetime import datetime
#import urllib2

from xyz.daum.cafe import Cafe, Board, Article
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
articleclubalbum_html = open('tests/mock/article_clubalbum.html').read().decode('euckr')

CLUBALBUM_BOARD_URL   = 'http://cafe986.daum.net/_c21_/album_list?grpid=ccJT&fldid=_album'
CLUBALBUM_ARTICLE_URL = 'http://cafe986.daum.net/_c21_/album_read?grpid=ccJT&fldid=_album&page=1&prev_page=0&firstbbsdepth=&lastbbsdepth=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz&contentval=001EWzzzzzzzzzzzzzzzzzzzzzzzzz&datanum=4744&edge=&listnum=15'

def urlread_side_effect(*args, **kwargs):
    url = args[0]
    if url == 'http://cafe.daum.net/loveclimb':
        return loveclimb_html
    elif url == 'http://cafe986.daum.net/_c21_/home?grpid=ccJT':
        return maininner_html
    elif url.startswith('http://cafe986.daum.net/_c21_/bbs_menu_ajax?grpid=ccJT'):
        return bbsmenu_html
    elif url == CLUBALBUM_BOARD_URL:
        return boardclubalbum_html
    elif url == CLUBALBUM_ARTICLE_URL:
        return articleclubalbum_html


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



class CafeBoardsTestCase(unittest.TestCase):
    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_called_boards_should_have_url(self, urlread_):
        cafe = Cafe('loveclimb')
        board = [b for b in cafe.boards if b.name == u'클럽앨범'][0]
        nt.eq_(board.url, CLUBALBUM_BOARD_URL)

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_called_baords_should_have_list_of_articles(self, urlread_):
        cafe = Cafe('loveclimb')
        board = [b for b in cafe.boards if b.name == u'클럽앨범'][0]
        nt.assert_true(len(board.articles) >= 0)

class BoardTestCase(unittest.TestCase):
    def test_should_have_url(self):
        # only url: ok
        Board(url=CLUBALBUM_BOARD_URL)

        # only name: not ok
        with nt.assert_raises(Exception):
            Board(name='u클럽앨범')

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
        board = Board(url=CLUBALBUM_BOARD_URL)
        article = [a for a in board.articles if a.title.startswith(u'0704 이대')][0]
        nt.eq_(article.url, CLUBALBUM_ARTICLE_URL)

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

        # has 7 comments
        nt.eq_(len(article.comments), 7)

        # parses correctly
        comment = [c for c in article.comments][0]
        nt.eq_(comment.nickname, u'강혜경')
        nt.eq_(comment.date, datetime(2012, 7, 5, 10, 21)) # 12.07.05 10:21
        nt.eq_(comment.content, u'아애들 너무 이쁘네요~~~쌤하고 종신선배 너무 좋으셨겠어요!')


#class CommentsTestCase(unittest.TestCase):
#    def test_parsing_comments




if __name__ == '__main__':
    unittest.main()

