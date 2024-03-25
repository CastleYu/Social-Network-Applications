import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from config import *


class Browser:
    def __init__(self, profile):
        # print(f'创建一个{profile}的Browser')
        self.profile = profile
        self.driver = None
        self.driver: WebDriver

    def start(self):
        raise NotImplementedError

    def get(self, url):
        if self.driver:
            self.driver.get(url)

    def get_current_url(self):
        if self.driver:
            return self.driver.current_url
        return None

    def get_cookies(self):
        if self.driver:
            return {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
        return None

    def get_cookie_by_name(self, name):
        if self.driver:
            return self.get_cookies().get(name, None)
        return None

    def maximize_window(self):
        if self.driver:
            self.driver.maximize_window()

    def minimize_window(self):
        if self.driver:
            self.driver.minimize_window()

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None


class ChromeBrowser(Browser):
    """ChromeSelenium的封装，提供启动、配置等功能。"""

    def __init__(self, profile='default'):
        super().__init__(profile)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def __get_chrome_user_data_dir():
        """获取Chrome用户数据目录的路径"""
        return BROWSER_USER_PROFILE_PATH_F.get('chrome').format(os.getlogin())

    def __config_chrome_options(self):
        """配置Chrome选项"""
        chrome_options = Options()
        if self.profile == 'user':
            chrome_options.add_argument("user-data-dir=" + self.__get_chrome_user_data_dir())
        elif self.profile == 'default':
            chrome_options.add_argument("profile-directory=Default")
        elif self.profile == 'test':
            test_path = os.path.join('test', 'profile')
            os.makedirs(test_path) if not os.path.exists(test_path) else None
            chrome_options.add_argument('user-data-dir=' + os.path.abspath(test_path))
        return chrome_options

    def start(self):
        if not self.driver:
            try:
                # print(f'以{self.profile}配置文件启动')
                self.driver = webdriver.Chrome(options=self.__config_chrome_options())
            except Exception as e:
                print("Error starting the Chrome WebDriver:", e)
