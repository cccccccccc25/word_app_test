import time
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DamaiMobileBot:
    def __init__(self, config):
        self.config = config
        self.driver = self._init_driver()
        self.wait = WebDriverWait(self.driver, 15)

    def _init_driver(self):
        desired_caps = {
            "platformName": "Android",
            "deviceName": self.config.get("device_name", "emulator-5554"),
            "appPackage": "com.damai.android",
            "appActivity": "com.damai.android.common.MainActivity",
            "noReset": True,
            "automationName": "UiAutomator2",
            "newCommandTimeout": 600,
            "uiautomator2ServerInstallTimeout": 20000
        }
        
        server_url = self.config.get("server_url", "http://127.0.0.1:4723/wd/hub")
        return webdriver.Remote(server_url, desired_caps)

    def _wait_element(self, by, value, timeout=15):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except Exception as e:
            print(f"等待元素失败: {value}")
            return None

    def _click_element(self, by, value):
        element = self._wait_element(by, value