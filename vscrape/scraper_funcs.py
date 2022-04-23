import re, time, logging
from typing import Optional
from settings import email, password, total_employees, company_url
# undetected chromedriver so my account stops getting locked
import undetected_chromedriver as uc
# selenium imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# basic logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# creates a driver for each thread to use
def create_driver() -> uc.Chrome:
    driver = uc.Chrome()
    driver.implicitly_wait(3)
    driver.maximize_window()
    return driver

# Logs in from the home page (fastest method)
def login_from_home(driver: uc.Chrome, *, email:str=email, password:str=password) -> None:
    logging.info('Logging in...')
    # make sure you're at the right link
    if driver.current_url != 'https://www.linkedin.com/': driver.get('https://www.linkedin.com/')
    # type in email and passsword
    driver.find_element(By.ID, 'session_key').send_keys(email)
    driver.find_element(By.ID, 'session_password').send_keys(password)
    # click the sign-in button
    driver.find_element(By.CLASS_NAME, "sign-in-form__submit-button").click()
    # check for captcha
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'captcha-internal')))
        logging.info('Captcha detected. Handle manually.')
        time.sleep(10)
    except Exception as e:
        logging.info('No captcha detected.')
    finally:
        driver.switch_to.default_content()
    # if driver.find_elements(By.ID, 'captcha-internal'):
    #     logging.info('Captcha detected, please handle manually')
    #     time.sleep(10)
    #     # switch the driver frame so that it's no longer in the iframe
        # driver.switch_to.default_content()

# Get a list of public profiles on the company page
def extract_company_employees(driver: uc.Chrome, url:str=company_url, *, total_employees:int=total_employees, return_profiles:bool=False) -> Optional[list[str]]:
    if not re.match(r'people/?$', url): 
        url += 'people/'
    driver.get(url)
    # wait for div with all the profiles to load
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'scaffold-finite-scroll')))
    except Exception as e:
        logging.error(f'Error loading profiles page: {e}')
        return None
    '''
    Gets & stores all visible & public employees. Whenever it runs out of visible employees, 
    it will scroll down to load more. Continues until it collects links for the given number of employees.
    ---
    @param get_all: True if you want to get all public employees, even those w/o a profile pic
    @param total_employees: the number of employees you want to get
    @param return_profiles: True if you want to return a list of all the profiles
    '''
    # get the initial list of people on the page
    profiles = driver.find_elements(By.XPATH, '//div[@class="scaffold-finite-scroll__content"]/ul/li')
    public_profiles = list()
    # extract all the profiles continually
    count = 0
    # check that it didn't top out more than twice in a row
    stalled = 0
    while len(public_profiles) < total_employees:
        for employee in profiles[count:]:
            # we know theyre private if they don't have a name
            if employee.text.startswith('LinkedIn'):
                continue
            # get the profile link
            try:
                profile_link = employee.find_element(By.CLASS_NAME, 'link-without-visited-state').get_attribute('href')
            except Exception as e:
                logging.error(f'Error getting profile link: {e}')
                continue
            public_profiles.append(profile_link)
            logging.info(f'{len(public_profiles)} profiles collected')
        # increase the count 
        count = len(profiles)
        # scroll up a little bit before scrolling to the bottom
        driver.execute_script('window.scrollBy(0, -100)')
        # scroll down to load more profiles
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        # wait for the new profiles to load
        time.sleep(1)
        # get the new profiles
        profiles = driver.find_elements(By.XPATH, '//div[@class="scaffold-finite-scroll__content"]/ul/li')
        # check if the profiles are the same as the last time
        if profiles == public_profiles:
            # if they are, it's likely that there are no more profiles
            # so we'll break out of the loop
            stalled += 1
            if stalled > 2:
                logging.info('Stalled on loading profiles, breaking out of loop')
                break
        else:
            # reset the stall counter
            stalled = 0
    # write the list of profiles to a file
    with open('profiles.txt', 'w') as f:
        for profile in public_profiles[:total_employees]:
            f.write(f'{profile}\n')
    logging.info(f'{total_employees} profiles stored')
    if return_profiles:
        return public_profiles

if __name__ == '__main__':
    # create a driver for each thread
    driver = create_driver()
    # login from the home page
    login_from_home(driver)
    # get the list of public profiles
    profiles = extract_company_employees(driver, total_employees=total_employees, return_profiles=True)
    # close the driver
    driver.quit()