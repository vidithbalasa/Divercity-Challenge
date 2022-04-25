import time, logging
# default values
from .settings import emails, passwords
# undetected chromedriver so my account stops getting locked
import undetected_chromedriver as uc
# selenium imports
from selenium.webdriver.common.by import By

# creates a driver for each thread to use
def create_driver(headless:bool=False) -> uc.Chrome:
    options = uc.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    # view the headless session through local host
    options.add_argument('--remote-debugging-port=9222')
    driver = uc.Chrome(options=options)
    driver.maximize_window()
    return driver

# checks if a captcha popped up on the screen
def check_for_captcha(driver: uc.Chrome) -> bool:
    if driver.find_elements(By.ID, 'CaptchaFrame'):
        logging.info('Captcha detected. Handle manually.')
        time.sleep(10)
        return True
    return False

# checks if one of those compliance messages with the check box pops up
def check_for_compliance(driver: uc.Chrome) -> bool:
    if (x:=driver.find_elements(By.CLASS_NAME, 'form__label')):
        if x.text.strip().startswith("I won't use tools that"):
            logging.info('Compliance detected. Handle manually.')
            time.sleep(10)
            return True
    return False

# Logs in from the home page (fastest method)
def login_through_form(driver: uc.Chrome, *, email:str=emails[0], password:str=passwords[0], from_homepage:bool=False) -> None:
    logging.info('Logging in...')
    # make sure you're at the right link
    if from_homepage: 
        driver.get('https://www.linkedin.com/')
    # type in email and passsword
    driver.find_element(By.ID, 'session_key').send_keys(email)
    driver.find_element(By.ID, 'session_password').send_keys(password)
    # click the sign-in button
    driver.find_element(By.CLASS_NAME, "sign-in-form__submit-button").click()
    check_for_captcha(driver)
    # # check for captcha
    # try:
    #     WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'captcha-internal')))
    # except Exception as _:
    #     logging.info('No captcha detected.')
    # else:
    #     logging.info('Captcha detected. Handle manually.')
    #     time.sleep(10)
    # finally:
    #     driver.switch_to.default_content()