#!/usr/bin/python


import urllib


def querydecode(s):
    ''' decode urlencoded query string and return dictionary '''
    s = s.lstrip('?')
    kvlist = [tuple(keyvalue.split('=')) for keyvalue in s.split('&')]
    return dict((k,urllib.unquote_plus(v))  for k,v in kvlist)

def include_dict(larger, smaller):
    for k,v in smaller.iteritems():
        if larger[k] != v:
            return False
    return True


# vim: sts=4 et
