#!/usr/bin/python
import urllib2
import httplib
import urlparse
import htmlentitydefs
import re

ARTICLE_TIMEOUTS = [15,30,60]

def urlopen(url, timeouts=None, data=None):
    '''request url open, retrying on timeout. '''
    timeouts = timeouts or [300, 300, 300] # default to wait 5 minutes 3 times

    last_exception = None
    for timeout in timeouts:
        try:
            # make request
            req  = urllib2.Request(url)
            # send request
            site = urllib2.urlopen(req, data, timeout=timeout)

            return site

        # retry on timeout
        except IOError as e:
            last_exception = e
            continue
        except httplib.HTTPException as e:
            last_exception = e
            continue
    # all retries failed
    else:
        raise last_exception

def urlread(url, timeouts=None):
    ''' open url and read the text, decoding with its encoding from header '''
    site = urlopen(url, timeouts=timeouts)
    text = site.read()
    encoding = get_encoding_from_header(site.headers)
    return text.decode(encoding)

def get_encoding_from_header(header=None, url=None):
    ''' either header or url must be provided '''
    if header is None:
        site = urlopen(url, timeouts=ARTICLE_TIMEOUTS)
        header = site.headers
    ct = header.dict['content-type'].strip()
    param = ct.split(';', 1)[1].strip()
    encoding = param.partition('charset=')[2]
    return encoding

def get_domain(url, path=None):
    '''
        urlparse:
            <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    '''
    parse_result = urlparse.urlparse(url)
    domain = '''%(scheme)s://%(netloc)s''' % parse_result._asdict()
    domain = domain.rstrip('/')

    # paste path if any
    if path:
        return domain + "/" + unescape(path).lstrip('/')

    return domain

def unescape(text, repeat=None):
    '''robust unescape.
    from http://effbot.org/zone/re-sub.htm#unescape-html '''
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    new_text = re.sub("&#?\w+;", fixup, text)

    # once
    if repeat is None:
        return new_text

    # repeat for specified times, until no change
    repeat_count = 0
    while new_text != text:
        text = new_text
        new_text = re.sub("&#?\w+;", fixup, text)

        repeat_count += 1
        if repeat is True: 
            continue
        elif repeat_count >= repeat:
            break

    return new_text

# vim: sts=4 et
