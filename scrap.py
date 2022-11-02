import time
from multiprocessing import freeze_support

path = r".\chromedriver_97.0.4692.99.exe"
url = 'https://instagram.com/stories/battlerigs/2961784597757525872?utm_source=ig_story_item_share&igshid=MDJmNzVkMjY='
# url= 'http://www.google.com'

from selenium.webdriver import Chrome, ChromeOptions


def create_browser():
    chrome_options = ChromeOptions()
    # 屏蔽webdriver特征方法1,高版本
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    # 屏蔽屏蔽自动化受控提示,webdriver version>76
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    return Chrome(executable_path=path, options=chrome_options)


def login():
    try:
        browser = create_browser()
        browser.get(url)
        time.sleep(15000)
        account = '//*[@id="loginForm"]/div/div[1]/div/label/input'
        pwd = '//*[@id="loginForm"]/div/div[2]/div/label/input'
        btn = '//*[@id="loginForm"]/div/div[3]'

        acc = 'xxfffoopp'
        pwd_msg = 'qwer147258'


        account_ele = browser.find_element_by_xpath(account)
        account_ele.send_keys(acc)

        pwd_ele = browser.find_element_by_xpath(pwd)
        pwd_ele.send_keys(pwd_msg)

        btn_ele = browser.find_element_by_xpath(btn)
        btn_ele.click()

        time.sleep(5)
        save_ele = browser.find_element_by_css_selector('button[class="_acan _acap _acas"]')
        save_ele.click()

        time.sleep(5)
        # time.sleep(1000)
        look_ele = browser.find_element_by_css_selector('button[class="_acan _acap _acau _acav"]')
        look_ele.click()
        time.sleep(5)
        time.sleep(20 * 3600)

    except:
        import traceback
        traceback.print_exc()


login()

# import undetected_chromedriver as uc
#
# if __name__ == '__main__':
#     freeze_support()
#     driver = uc.Chrome(
#         # browser_executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#                        driver_executable_path=path)
#     resp = driver.get(url)
#     print(resp)
