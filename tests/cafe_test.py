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

class FakeResponse:
    def __init__(self, html, status=200, **kwargs):
        self.dict = kwargs
        self.__html = html
        self.status = status
        self.headers = {}
    def read(self):
        return self.__html
loveclimb_html = open('tests/mock/loveclimb.html').read()
maininner_html = open('tests/mock/home_grpid_ccJT.html').read()
bbsmenu_html   = open('tests/mock/bbs_menu_ajax_ccJT.html').read().decode('utf8')


class CafeTestCase(unittest.TestCase):
    def test_receives_domain_as_argument(self):
        cafe = Cafe('loveclimb')
        nt.eq_(cafe.domain, 'loveclimb')

    @mock.patch('xyz.daum.cafe.urlread')
    def test_boards_returns_objects_with_name(self, urlread_):
        urlread_.side_effect = [loveclimb_html,maininner_html,bbsmenu_html]

        cafe = Cafe('loveclimb')
        for b in cafe.boards:
            b.name

    @mock.patch('xyz.daum.cafe.urlread')
    def test_first_call_to_boards_calls_http_request(self, urlread_):
        '''
            calls: cafe.url
            calls: cafe.inner_url
            calls: cafe.sidebar_url
        '''
        urlread_.return_value = loveclimb_html
        urlread_.side_effect = [loveclimb_html,maininner_html,bbsmenu_html]

        #
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


    @mock.patch('xyz.daum.cafe.urlread')
    def test_get_board_names(self, urlread_):
        urlread_.return_value = loveclimb_html
        urlread_.side_effect = [loveclimb_html,maininner_html,bbsmenu_html]

        BOARD_NAMES = [
            u'최신글 보기', u'더탑 소개', u'클라이밍 전과 후 무엇이 달라졌을까?', u'가입인사. 등업신청', u'이런말 저런말', u'한 줄 메모장', u'오늘은 무슨일이?(회원소식)', u'산모임더탑 소식', u'등반 기록', u'THE TOP 등반교실', u'THE TOP 암.빙벽반 수료', u'단체강습일정', u'등반/산행계획', u'등반/산행후기', u'클럽앨범', u'산 속 프라이팬', u'클라이밍 정보', u'클라이밍동영상', u'건강.다이어트 정보', u'스팸 신고', u'Squamish', u'Bugaboo', u'Skaha', u'안나푸르나', u'파타고니아', u'리우데자네이루', u'크라비', u'2012크라비 등반', u'Q&A질의란', u'지식인에게 물어봐 주세요', u'대기! [잠시 쉼]', u'카페파이', u'인기글 보기', u'이미지 보기', u'동영상 보기', u'투표',
        ]
        #
        cafe = Cafe('loveclimb')
        board_names = sorted(b.name for b in cafe.boards)
        nt.eq_(board_names, sorted(BOARD_NAMES))



class CafeAcceptanceTestCase(unittest.TestCase):
    def test_get_board_names(self):
        BOARD_NAMES = ['최신글 보기', 'THE TOP', '더탑 소개', 'Before & After', '클라이밍 전과 후 무엇이 달라졌을까?', 'THE TOP 人', '가입인사. 등업신청', '이런말 저런말', '한 줄 메모장', '오늘은 무슨일이?(회원소식)', '산모임더탑 소식', '등반 기록', 'THE TOP 교육', 'THE TOP 등반교실', 'THE TOP 암.빙벽반 수료', '단체강습일정', 'THE TOP 山', '등반/산행계획', '등반/산행후기', '클럽앨범', '산 속 프라이팬', 'THE TOP 공부방', '클라이밍 정보', '클라이밍동영상', '건강.다이어트 정보', '스팸 신고', 'THE TOP 해외등반', 'Squamish', 'Bugaboo', 'Skaha', '안나푸르나', '파타고니아', '리우데자네이루', '크라비', '2012크라비 등반', '투표', 'Q&A질의란', '지식인에게 물어봐 주세요', '대기! [잠시 쉼]', '카페파이', '인기글 보기', '이미지 보기', '동영상 보기']
        #
        board_names = sorted(b.name for b in Cafe('loveclimb').boards)
        nt.eq_(board_names, sorted(BOARD_NAMES))



if __name__ == '__main__':
    unittest.main()
