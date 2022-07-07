#-*-coding:gbk-*-
import login
import sign


def main():
    cookie = login.get_cookie()
    if (cookie == None):
        print('登录失败')
    else:
        sign.run(cookie)


if __name__ == '__main__':
    main()