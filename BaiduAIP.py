# -*- coding: utf-8 -*-
from aip import AipOcr

""" 你的 APPID AK SK """
APP_ID = '15927274'
API_KEY = 'wutPhQANL3aOBuXbP8SnWyrP'
SECRET_KEY = '14snx1YG8TP8eGVQlWsteltFX6DGGebD'


class BaiduAIP(object):
    def __init__(self):
        self.client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    # 读取图片文件
    # 返回二进制内容
    def get_file_content(self, file_path):
        with open(file_path, 'rb') as fp:
            return fp.read()

    # 调用百度AIP并解析接口返回数据
    # 返回多个内容 => 重做
    # 平均值小于0.8 => 重做
    # 成功 => 返回code
    def get_code(self):
        # image = self.get_file_content(self.picture_path)

        """ 如果有可选参数 """
        options = {"language_type": "ENG", "detect_direction": "true", "detect_language": "true", "probability": "true"}
        response = self.client.basicGeneralUrl(self.picture_path, options)
        print(response, self.picture_path)
        data = response
        if isinstance(data['words_result'], list) and data['words_result'].__len__() == 1:
            if data['words_result'][0]['probability']['average'] > 0.7: # 准确率达到0.7以上
                return data['words_result'][0]['words']
            else:
                return 'do again'
        else:
            return 'do again'
