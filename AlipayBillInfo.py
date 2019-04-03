# -*- coding: utf-8 -*-
'''
尝试登录支付宝
并获取账单记录

通过 seleium 登录支付宝，
获取 cookies
'''

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from BaiduAIP import BaiduAIP

# 登录 url
Login_Url = "https://auth.alipay.com/login/index.htm?goto=https%3A%2F%2Fwww.alipay.com%2F"
# 账单 url
Bill_Url = "https://consumeprod.alipay.com/record/standard.htm"

# 登录用户名和密码
USERNMAE = ""
PASSWD = ""

# 自定义 headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Referer": "https://consumeprod.alipay.com/record/advanced.htm",
    "Host": "consumeprod.alipay.com",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive"
}


def snap(sel):
    # 截图查看
    sel.save_screenshot("./asset/" + str(time.clock()) + ".png")


class Alipay_Bill_Info(object):
    '''支付宝账单信息'''

    def __init__(self, headers, user, passwd):
        '''
        类的初始化

        headers：请求头
        cookies: 持久化访问
        info_list: 存储账单信息的列表
        '''
        self.headers = headers
        # 初始化用户名和密码
        self.user = user
        self.passwd = passwd
        # 利用 requests 库构造持久化请求
        self.session = requests.Session()
        # 将请求头添加到缓存之中
        self.session.headers = self.headers
        # 初始化存储列表
        self.info_list = []
        self.baiduAIP = BaiduAIP()

    def wait_input(self, ele, str):
        '''减慢账号密码的输入速度'''
        for i in str:
            ele.send_keys(i)
            time.sleep(0.5)

    def get_cookies(self):
        '''获取 cookies'''

        # 查看当前session是否包含cookie
        cookie = self.session.cookies

        # 初始化浏览器对象
        sel = webdriver.PhantomJS()
        sel.maximize_window()
        sel.get(Login_Url)
        sel.implicitly_wait(3)

        # 找到账号密码登录
        login_interface = sel.find_element_by_xpath("//*[@id='J-loginMethod-tabs']/li[2]")
        login_interface.click()  # 点击
        # 截图查看
        # snap(sel)
        time.sleep(2)

        # 找到用户名字输入框
        uname = sel.find_element_by_id("J-input-user")
        uname.clear()
        print("正在输入账号.....")
        self.wait_input(uname, self.user)
        time.sleep(1)

        # 找到密码输入框
        upass = sel.find_element_by_id("password_rsainput")
        upass.clear()
        print("正在输入密码....")
        self.wait_input(upass, self.passwd)

        # 判断是否需要输入验证码
        check_code = sel.find_element_by_id("J-checkcode")
        check_class = check_code.get_attribute("class")
        print(check_class, "fn_hidden" not in check_class)
        if "fn-hide" not in check_class:
            # 需要输入验证码
            snap(sel)
            i = 0
            code = ''
            while i < 10:
                i+=1
                print('code', code)
                if code == '': # 第一次
                    ucheckimg = sel.find_element_by_id("J-checkcode-img")
                    picture_src = ucheckimg.get_attribute("src")
                    self.baiduAIP.picture_path = picture_src
                    code = self.baiduAIP.get_code()
                elif code == 'do again':  # 未成功识别
                    ucheckimg = sel.find_element_by_id("J-checkcode-img")
                    ucheckimg.click()  # 点击验证码，重新获取验证码
                    ucheckimg = sel.find_element_by_id("J-checkcode-img")
                    picture_src = ucheckimg.get_attribute("src")
                    self.baiduAIP.picture_path = picture_src
                    code = self.baiduAIP.get_code()
                else: # 成功识别
                    break

            if code != 'do again':
                ucheck = sel.find_element_by_id("J-input-checkcode")
                ucheck.clear()
                print('正在输入验证码...')
                self.wait_input(ucheck, code)

        snap(sel)
        # 找到登录按钮
        # button = sel.find_element_by_id("J-login-btn")
        # time.sleep(1)
        # button.click()

        # 跳转到账单页面
        # print("正在跳转页面....")
        # sel.get(Bill_Url)
        # sel.implicitly_wait(3)

        # snap(sel)
        # 获取 cookies 并转换为字典类型
        cookies = sel.get_cookies()
        cookies_dict = {}
        for cookie in cookies:
            if "name" in cookie and "value" in cookie:
                cookies_dict[cookie["name"]] = cookie["value"]

        return cookies_dict

        # 关闭浏览器
        sel.close()

    def set_cookies(self):
        '''将获取到的 cookies 加入 session'''
        c = self.get_cookies()
        self.session.cookies.update(c)
        print(self.session.cookies)

    def login_status(self):
        """判断登录状态"""
        # 添加 cookies
        self.set_cookies()
        status = self.session.get(
            Bill_Url, timeout=5, allow_redirects=False).status_code
        print(status)
        if status == 200:
            return True
        else:
            # cookie 失效
            self.session.cookies.update(None)
            return False

    def get_data(self):
        """
        利用 bs4 库解析 html
        并抓取数据，
        数据以字典格式保存在列表里
        """
        status = self.login_status()
        if status:
            html = self.session.get(Bill_Url).text
            soup = BeautifulSoup(html, "lxml")
            # 抓取前五个交易记录
            trades = soup.find_all("tr", class_="J-item ")[:5]

            for trade in trades:
                # 做一个 try except 避免异常中断
                try:
                    # 分别找到账单的 时间 金额 以及流水号
                    time = trade.find("p", class_="text-muted").text.strip()
                    amount = trade.find(
                        "span", class_="amount-pay").text.strip()
                    code = trade.find(
                        "a", class_="J-tradeNo-copy J-tradeNo")["title"]
                    self.info_list.append(
                        dict(time=time, amount=amount, code=code))
                except:
                    self.info_list.append({"error": "出现错误"})

        else:
            self.info_list.append({"error": "出现错误"})
        return self.info_list
