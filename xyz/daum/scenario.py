#!/usr/bin/python
import datetime

from xyz import daum

'''

'''

def update_last_runtime(dt): print 'saving last runtime to storage..'
def load_last_runtime():
    print 'loading last runtime from storage..'
    return datetime.datetime.now()
def save(comment): print 'saving comment to storage: ' + comment


def run():
    if not daum.is_logged_in():
        user = daum.login('jangxyz', password='XXXXX')


    #cafe = user.find_cafe(name='더탑')
    cafe = user.find_cafe_by_name('더탑')
    if not cafe:
        cafe = user.find_cafes_by_partial_name('더탑')[0]

    last_run_time = load_last_runtime()

    for board in cafe.boards:
    #for board_name in []:
    #    board = cafe.find_board_by_name(board_name)
        for article in board.get_latest_articles(20):
            #comments = article.fetch_comments()
            comments = article.comments
            recent_comments = [c for c in comments if c.created_at > last_run_time]
            for comment in recent_comments:
                save(comment)

    update_last_runtime(datetime.datetime.now())


# vim: sts=4 et
