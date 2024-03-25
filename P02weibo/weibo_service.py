import time

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from browser import *
from config import *
from utils import show_image_by_url


class WeiboService(ChromeBrowser):
    def __init__(self, profile='test'):
        super().__init__(profile)

    def preconditional_click(self, precondition_list: list):
        """前置条件点击"""
        for feature_dict in precondition_list:
            for by, value in feature_dict.items():
                try:
                    elem = self.driver.find_element(by, value)
                    try:
                        elem.click()
                        return True
                    except Exception as e:
                        print(e)
                        print("When processing preconditional click:")
                        print("\tElement founded, but error occurred when trying to click")
                        if input('Press Enter to Finish Preconditional Click') == '':
                            return False
                        else:
                            continue
                except NoSuchElementException:
                    continue
        else:
            raise KeyError("There is a preconditional click, but no element founded")

    def find_elemnet_by_dict(self, feature_dict: dict):
        # 处理前置条件点击，并且记录Flag-是否处理
        precondition = feature_dict.pop(PRECONDITION, None)
        print(precondition)
        if precondition:
            prec_did = self.preconditional_click(precondition)
        else:
            prec_did = True

        # 遍历寻找可用的键值对来寻找元素
        for by, value in feature_dict.items():
            try:
                elem = self.driver.find_element(by, value)
                return elem
            except NoSuchElementException:
                continue
        else:  # 未寻得报错
            if prec_did:
                raise KeyError("No element founded")
            else:
                raise KeyError("No element founded, and no preconditional click")

    # def monitor_page_change(self, initial_url='', to_be_url=''):
    #     if initial_url and to_be_url:
    #         return ValueError('Provide both initial_url and to_be_url')
    #     pass

    def login(self, username=None, password=None, use_qr_code=True):
        self.try_login(0, username, password, use_qr_code)

    def try_login(self, index=0, username=None, password=None, use_qr_code=True):
        method = LOGIN_METHODS[index]
        url = method.get(URL)
        self.get(url)
        if use_qr_code:
            feature_dict = method.get(QRCODE)
            elemnet = self.find_elemnet_by_dict(feature_dict)
            img_url = elemnet.get_attribute('src')
            show_image_by_url(img_url)
            try:
                # 等待直到URL变为特定值
                WebDriverWait(self.driver, 30).until(EC.url_contains("weibo.com/u/"))
                print("URL 变化到了期望的地址。")
            except TimeoutException:
                print("在指定时间内URL没有变化。")


if __name__ == "__main__":
    weibo_service = WeiboService('default')
    weibo_service.start()
    weibo_service.login()
