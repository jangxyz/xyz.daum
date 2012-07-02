# -*- coding: utf8 -*-

import unittest
from nose import tools as nt
import mock

import urlparse
#import urllib2

from xyz.daum.cafe import Cafe
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

def urlread_side_effect(*args, **kwargs):
    url = args[0]
    if url == 'http://cafe.daum.net/loveclimb':
        return loveclimb_html
    elif url == 'http://cafe986.daum.net/_c21_/home?grpid=ccJT':
        return maininner_html
    elif url.startswith('http://cafe986.daum.net/_c21_/bbs_menu_ajax?grpid=ccJT'):
        return bbsmenu_html


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
    def test_calling_board_runs_once(self, urlread_):
        # call boards twice
        cafe = Cafe('loveclimb')
        [b.name for b in cafe.boards]
        [b.name for b in cafe.boards]

        # call to cafe.url should only be called once
        called_urls = [c[0][0] for c in urlread_.call_args_list]
        nt.eq_(called_urls.count(cafe.url), 1)



class BoardTestCase(unittest.TestCase):
    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_has_url(self, urlread_):
        cafe = Cafe('loveclimb')
        board = [b for b in cafe.boards if b.name == u'클럽앨범'][0]
        nt.eq_(board.url, 'http://cafe986.daum.net/_c21_/album_list?grpid=ccJT&fldid=_album')

    @mock.patch('xyz.daum.cafe.urlread', side_effect=urlread_side_effect)
    def test_has_list_of_articles(self, urlread_):
        cafe = Cafe('loveclimb')
        board = [b for b in cafe.boards if b.name == u'클럽앨범'][0]
        nt.assert_true(len(board.articles) >= 0)


class CafeAcceptanceTestCase(unittest.TestCase):
    def test_get_board_names(self):
        BOARD_NAMES = [
            u'최신글 보기', u'더탑 소개', u'클라이밍 전과 후 무엇이 달라졌을까?', u'가입인사. 등업신청', u'이런말 저런말', u'한 줄 메모장', u'오늘은 무슨일이?(회원소식)', u'산모임더탑 소식', u'등반 기록', u'THE TOP 등반교실', u'THE TOP 암.빙벽반 수료', u'단체강습일정', u'등반/산행계획', u'등반/산행후기', u'클럽앨범', u'산 속 프라이팬', u'클라이밍 정보', u'클라이밍동영상', u'건강.다이어트 정보', u'스팸 신고', u'Squamish', u'Bugaboo', u'Skaha', u'안나푸르나', u'파타고니아', u'리우데자네이루', u'크라비', u'2012크라비 등반', u'Q&A질의란', u'지식인에게 물어봐 주세요', u'대기! [잠시 쉼]', u'카페파이', u'인기글 보기', u'이미지 보기', u'동영상 보기', u'투표', ]
        #
        board_names = sorted(b.name for b in Cafe('loveclimb').boards)
        nt.eq_(board_names, sorted(BOARD_NAMES))



if __name__ == '__main__':
    unittest.main()

