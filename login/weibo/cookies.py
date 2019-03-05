from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import BytesIO
from PIL import Image
import time
from login.weibo.chaojiying import Chaojiying_Client
import random

# 超级鹰用户名、密码、软件ID、验证码类型
CHAOJIYING_USERNAME = 'Tiezhugg'
CHAOJIYING_PASSWORD = 'lhf101400'
CHAOJIYING_SOFT_ID = 898726
CHAOJIYING_KIND = 9004


class WeiboCookies():
    def __init__(self, username, password, browser):
        self.url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https://m.weibo.cn/'
        self.browser = browser
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password
        self.chaojiying = Chaojiying_Client(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)

    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        self.browser.delete_all_cookies()
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        time.sleep(random.random() + 0.8)
        submit.click()

    def get_button(self):
        """
        获取初始验证按钮
        :return: 按钮对象
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
        return button

    def get_click_element(self):
        '''
        获取验证码图片对象
        :return: 图片对象
        '''
        img_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_item_wrap')))
        return img_element

    def get_screenshot(self):
        '''
        获取整个网页截图
        :return: 截图对象
        '''
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_position(self):
        '''
        获取验证码图片位置
        :return: 验证码位置元组
        '''
        img = self.get_click_element()
        time.sleep(2)
        # 获取图片的位置
        location = img.location
        # 获取图片的尺寸
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size['width']
        return (top, bottom, left, right)

    def get_geetest_image(self, name='captcha.png'):
        '''
        通过网页截图截取验证码图片
        :return: 图片对象
        '''
        top, bottom, left, right = self.get_position()
        print('验证码图片位置：', top, bottom, left, right)
        screenshot = self.get_screenshot()
        # 截图验证码图片
        captcha = screenshot.crop((left, top, right, bottom))
        return captcha

    def get_points(self, captcha_result):
        '''
        解析识别结果
        :param captcha_result: 识别结果
        :return:  转化后的结果
        '''
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations

    def touch_click_words(self, locations):
        '''
        点击验证图片
        :param locations: 点击位置
        :return: None
        '''
        for location in locations:
            print('文字坐标:', location)
            ActionChains(self.browser).move_to_element_with_offset(self.get_click_element(), location[0],
                    location[1]).click().perform()
            time.sleep(random.random() + 1)

    def click_verify_button(self):
        '''
        点击验证按钮
        :return: 按钮对象
        '''
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip')))
        return button

    def login_successfully(self):
        """
        判断是否登录成功
        :return:
        """
        try:
            return bool(
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'lite-iconf-profile'))))
        except TimeoutException:
            return False

    def get_cookies(self):
        """
        获取Cookies
        :return:
        """
        return self.browser.get_cookies()

    def main(self):
        # 打开登录页面，输入用户信息后点击登录
        self.open()
        time.sleep(random.random() + 1)
        # 获取验证按钮并点击
        button = self.get_button()
        button.click()
        # 如果不需要验证码直接登录成功
        if self.login_successfully():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        # 如果有验证码，识别验证码
        image = self.get_geetest_image()
        bytes_array = BytesIO()
        image.save(bytes_array, format='PNG')
        captcha_result = self.chaojiying.PostPic(bytes_array.getvalue(), CHAOJIYING_KIND)
        print(captcha_result)
        locations = self.get_points(captcha_result)
        self.touch_click_words(locations)
        # 获取验证按钮
        verify_button = self.click_verify_button()
        verify_button.click()
        # 判断是否识别验证码成功后，成功登录微博
        if self.login_successfully():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        else:
            print('正在尝试重新登录')
            self.main()


if __name__ == '__main__':
    browser = webdriver.Chrome()
    result = WeiboCookies('anqolj010981@game.weibo.com', 'ifrc77555', browser).main()
    print(result)

