import requests
import urllib.parse
import json
from configparser import ConfigParser

LOGIN_URL = 'https://neau.campusphere.net/iap/login?service=https://neau.campusphere.net/portal/login'
DO_LOGIN_URL = 'https://neau.campusphere.net/iap/doLogin'
LT_URL = 'https://neau.campusphere.net/iap/security/lt'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'

req_body = {
    'username': '',
    'password': '',
    'rememberMe': False,
    'lt': '',
    'captcha': ''
}


def get_cookie():
    config = ConfigParser()
    config.read('user.conf', encoding='gbk')
    req_body['username'] = config['user']['username']
    req_body['password'] = config['user']['password']
    res = requests.get(LOGIN_URL, headers={'User-Agent': USER_AGENT}, allow_redirects=False)
    cookie = res.cookies
    redirect_url = res.headers['Location']
    _2lBepC = urllib.parse.parse_qs(urllib.parse.urlparse(redirect_url).query)['_2lBepC']
    res = requests.post(LT_URL, headers={'User-Agent': USER_AGENT}, cookies=cookie, data={'lt': _2lBepC})
    req_body['lt'] = json.loads(res.text)['result']['_lt']
    res = requests.post(DO_LOGIN_URL, headers={'User-Agent': USER_AGENT}, cookies=cookie, data=req_body,
                        allow_redirects=False)

    if (len(res.cookies) == 0):
        return
    else:
        redirect_url = res.headers['Location']
        cookie.update(res.cookies)
        res = requests.post(redirect_url, headers={'User-Agent': USER_AGENT}, cookies=cookie, allow_redirects=False)
        cookie.update(res.cookies)
        cookie_str = ''
        for item in cookie:
            cookie_str = cookie_str + item.name + '=' + item.value + ';'
        return cookie_str
