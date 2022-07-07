#-*-coding:utf8-*-
import requests
import json
import hashlib
import base64
import pyaes
from pyDes import des, CBC, PAD_PKCS5
from configparser import ConfigParser

SUBMIT_SIGN_URL = 'https://neau.campusphere.net/wec-counselor-sign-apps/stu/sign/submitSign'
SIGN_TASK_URL = 'https://neau.campusphere.net/wec-counselor-sign-apps/stu/sign/getStuSignInfosInOneDay'
DETAIL_SIGN_TASK_URL = 'https://neau.campusphere.net/wec-counselor-sign-apps/stu/sign/detailSignInstance'
DESKEY = 'b3L26XNL'
AESKEY = 'ytUQ7l2ZZu8mLvJZ'

user = {
    'username': '',
    'password': '',
    'lat': '',
    'lon': '',
    'position': '',
}

header = {
    'Host': 'neau.campusphere.net',
    'Accept': 'application/json, text/plain, */*',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json;charset=utf-8',
    'Origin': 'https://neau.campusphere.net',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 (4472147968)cpdaily/9.0.12  wisedu/9.0.12',
    'Connection': 'keep-alive',
    'Cookie': ''
}

lite_header = {
    'User-Agent': '%E4%BB%8A%E6%97%A5%E6%A0%A1%E5%9B%AD/1 CFNetwork/1312 Darwin/21.0.0',
    'Cpdaily-Extension': '',
    'Cookie': '',
}


def get_device_id(user):
    md5 = hashlib.md5()
    md5.update(user['username'].encode('utf8'))
    device_id = md5.hexdigest().upper()
    device_id = device_id[0:8] + '-' + device_id[8:12] + '-' + \
                device_id[12:16] + '-' + device_id[16:20] + '-' + device_id[20:32]
    return device_id


def get_cpdaily_extension(user):
    info = {
        "systemName": "iOS",
        "systemVersion": "15.0",
        "model": "iPhone11,2",
        "deviceId": user['deviceId'],
        "appVersion": '9.0.12',
        "lon": user['lon'],
        "lat": user['lat'],
        "userId": user['username'],
    }
    return des_encrypt(json.dumps(info), DESKEY)


def get_body_string(form):
    return aes_encrypt(json.dumps(form), AESKEY)


def get_sign(reqForm):
    form = {
        "appVersion": '9.0.12',
        "bodyString": reqForm['bodyString'],
        "deviceId": reqForm["deviceId"],
        "lat": reqForm["lat"],
        "lon": reqForm["lon"],
        "model": reqForm["model"],
        "systemName": reqForm["systemName"],
        "systemVersion": reqForm["systemVersion"],
        "userId": reqForm["userId"],
    }
    sign_str = ''
    for info in form:
        if sign_str:
            sign_str += '&'
        sign_str += "{}={}".format(info, form[info])
    sign_str += "&{}".format(AESKEY)
    return hashlib.md5(sign_str.encode()).hexdigest()


def get_req_form(user, form):
    req_form = {
        'appVersion': '9.0.12',
        'systemName': 'iOS',
        'bodyString': get_body_string(form),
        'lon': form['longitude'],
        'calVersion': 'firstv',
        'model': 'iPhone11,2',
        'systemVersion': '15.0',
        'deviceId': user['deviceId'],
        'userId': user['username'],
        'version': 'first_v2',
        'lat': form['latitude']
    }
    req_form['sign'] = get_sign(req_form)
    return req_form


def des_encrypt(s, key):
    iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    encrypt_str = k.encrypt(s)
    return base64.b64encode(encrypt_str).decode()


def aes_encrypt(s, key, iv=b'\x01\x02\x03\x04\x05\x06\x07\x08\t\x01\x02\x03\x04\x05\x06\x07'):
    encrypter = pyaes.Encrypter(
        pyaes.AESModeOfOperationCBC(key.encode('utf-8'), iv))
    encrypted = encrypter.feed(s)
    encrypted += encrypter.feed()
    return base64.b64encode(encrypted).decode()


def get_sign_task_info(user):
    header['Cookie'] = user['cookie']
    datas = json.loads(requests.post(url=SIGN_TASK_URL, json={}, headers=header).text)['datas']
    un_signed_tasks = datas['unSignedTasks']
    leave_tasks = datas['leaveTasks']
    for task in un_signed_tasks:
        if '东北农业大学学生健康信息上报' in task['taskName']:
            return {'signInstanceWid': task['signInstanceWid'], 'signWid': task['signWid']}
    for task in leave_tasks:
        if '东北农业大学学生健康信息上报' in task['taskName']:
            return {'signInstanceWid': task['signInstanceWid'], 'signWid': task['signWid']}
    return {'signInstanceWid': -1, 'signWid': -1}


def get_detail_task(user, signTaskInfo):
    header['Cookie'] = user['cookie']
    datas = json.loads(requests.post(url=DETAIL_SIGN_TASK_URL,
                                     json=signTaskInfo, headers=header).text)['datas']
    return datas


def get_answer_form(user, detailTask):
    form = {}
    extra_field = detailTask['extraField']
    form['signPhotoUrl'] = ''
    if detailTask['isNeedExtra']:
        form['isNeedExtra'] = 1
        extra_field_item_values = []
        for item in extra_field:
            extra_field_items = item['extraFieldItems']
            for option in extra_field_items:
                if option['isAbnormal'] == False:
                    extra_field_item_values.append(
                        {'extraFieldItemValue': option['content'], 'extraFieldItemWid': option['wid']})
                    break
        form['extraFieldItems'] = extra_field_item_values
    form['longitude'] = user['lon']
    form['latitude'] = user['lat']
    form['isMalposition'] = detailTask['isMalposition']
    form['abnormalReason'] = ''
    form['signInstanceWid'] = detailTask['signInstanceWid']
    form['position'] = user['position']
    form['uaIsCpadaily'] = True
    form['signVersion'] = '1.0.0'
    return form


def submit_task(cookie):
    user['cookie'] = cookie
    user['deviceId'] = get_device_id(user)
    sign_task_info = get_sign_task_info(user)
    if sign_task_info['signWid'] == -1:
        print('无签到任务')
        return
    form = get_req_form(user, get_answer_form(user, get_detail_task(user, sign_task_info)))
    lite_header['Cookie'] = user['cookie']
    lite_header['Cpdaily-Extension'] = get_cpdaily_extension(user)
    resBody = json.loads(requests.post(
        url=SUBMIT_SIGN_URL, json=form, headers=lite_header).text)
    if '任务未开始' in resBody['message']:
        print('任务未开始')
    else:
        print('SUCCESS')


def run(cookie):
    config = ConfigParser()
    config.read('user.conf')
    user['username'] = config['user']['username']
    user['password'] = config['user']['password']
    user['lat'] = config['user']['lat']
    user['lon'] = config['user']['lon']
    user['position'] = config['user']['position']
    submit_task(cookie)