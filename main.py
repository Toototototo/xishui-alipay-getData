# -*- coding: utf-8 -*-

from BaiduAIP import BaiduAIP
from AlipayBillInfo import Alipay_Bill_Info, HEADERS, USERNMAE, PASSWD

if __name__ == '__main__':
    alipay = Alipay_Bill_Info(headers=HEADERS, user=USERNMAE, passwd=PASSWD)
    alipay.get_cookies()
    print(alipay.__dict__)
