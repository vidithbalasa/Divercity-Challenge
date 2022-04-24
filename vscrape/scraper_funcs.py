import re, time, logging
from typing import Optional
import concurrent.futures
# default values
from settings import email, password, total_employees, company_url, num_threads
# undetected chromedriver so my account stops getting locked
import undetected_chromedriver as uc
# selenium imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
# beautiful soup imports
from bs4 import BeautifulSoup as bs
# data storage
from data_storage import Employees

# basic logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# creates a driver for each thread to use
def create_driver(headless:bool=False) -> uc.Chrome:
    # make it all pull from C:/temp/profile
    options = uc.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    # view the headless session through local host
    options.add_argument('--remote-debugging-port=9222')
    driver = uc.Chrome(options=options)
    driver.maximize_window()
    return driver

# Logs in from the home page (fastest method)
def login_through_form(driver: uc.Chrome, *, email:str=email, password:str=password, from_homepage:bool=False) -> None:
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

# Get a list of public profiles on the company page
def extract_company_employees(driver: uc.Chrome, *, url:str=company_url, total_employees:int=total_employees, return_profiles:bool=False) -> Optional[list[str]]:
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
                logging.error(f'Linkedin locked my account again. Won\'t display any more profiles')
                continue
            public_profiles.append(profile_link)
            logging.info(f'{len(public_profiles):03} profiles collected')
        # increase the count 
        count = len(profiles)
        # scroll up a little bit before scrolling to the bottom (makes sure it triggers the load more function)
        # increase the amount u scroll up each time it stalls
        driver.execute_script(f'window.scrollBy(0, {-300*(stalled+1)})')
        # scroll down to load more profiles
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        # wait for the new profiles to load
        time.sleep(0.4)
        # get the new profiles
        profiles = driver.find_elements(By.XPATH, '//div[@class="scaffold-finite-scroll__content"]/ul/li')
        # check if the profiles are the same as the last time
        if profiles == public_profiles:
            # if theyre the same, it's likely that there are no more profiles so we'll break out of the loop
            stalled += 1
            if stalled > 4:
                logging.info('Stalled on loading profiles, breaking out of loop')
                break
        else:
            # reset the stall counter
            stalled = 0
    # write the list of profiles to a file
    # with open('profiles.txt', 'w') as f:
    #     for profile in public_profiles[:total_employees]:
    #         f.write(f'{profile}\n')
    print(f"{'='*10}{total_employees} profiles stored{'='*10}")
    if return_profiles:
        return public_profiles

# get the info for a single profile
def extract_employee_info(driver: uc.Chrome, profile_link:str, employees: Employees) -> None:
    driver.get(profile_link)
    # wait for the profile to load
    check_for_captcha(driver)
    check_for_compliance(driver)
    # if theres a sign in form prompt, press the sign in button and run the login function
    if driver.find_elements(By.CLASS_NAME, 'join-form'):
        driver.find_element(By.CLASS_NAME, 'authwall-join-form__form-toggle--bottom').click()
        login_through_form(driver)
    # wait for the profile to load
    try:
        box = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'ph5')))
    except TimeoutException:
        if driver.find_elements(By.CLASS_NAME, 'join-form'):
            logging.info('Got logged out, logging back in...')
            return
        logging.error(f"Could not load profile info for {re.findall(r'https://www.linkedin.com/in/(.+)/', profile_link)[0]}")
        return
    # # get employee info with beautiful soup
    # soup = bs(driver.page_source, 'html.parser')
    # # get the name
    # first_name, last_name = soup.find('h1', {'class': 'text-heading-xlarge inline t-24 v-align-middle break-words'}).text.split(maxsplit=1)
    # # get the label
    # label = soup.find('div', {'class': 'text-body-medium break-words'}).text
    # # get the location
    # location = soup.find('span', {'class': 'text-body-small inline t-black--light break-words'}).text
    
    # extract profile info
    # get name
    first_name, last_name = box.find_element(By.TAG_NAME, 'h1').text.split(maxsplit=1)
    # get label
    label = box.find_element(By.CLASS_NAME, 'text-body-medium').text
    # get location
    location = box.find_element(By.CLASS_NAME, 'pb2').text
    # get profile picture
    # check that they don't have a ghost profile pic
    if box.find_elements(By.CLASS_NAME, 'ghost-person'):
        profile_pic = ''
    else:
        profile_pic = box.find_element(By.CLASS_NAME, 'pv-top-card-profile-picture__image').get_attribute('src')

    # store all this info in the employees object
    employees.add_employee(first_name, last_name, label=label, location=location, profile_pic=profile_pic)
    logging.info(f'{first_name} {last_name} added to employees: {employees[0].label}')

# a function that takes in a driver and a list of employees, it is a worker in charge of
# getting all the information for the given employees
def get_multiple_employee_data(driver: uc.Chrome, employees: list[str], employee_storage: Employees) -> None:
    # login_through_form(driver)
    for profile_link in employees:
        extract_employee_info(driver, profile_link, employee_storage)    

# concurrent function that runs extract_employee information on multiple threads
def get_all_employee_data(employees: list[str]) -> Employees:
    # # split up employees into a num_threads lists for each thread
    # employees = [employees[i::num_threads] for i in range(num_threads)]
    # employee_storage = Employees()
    # d = [create_driver(headless=True) for _ in range(num_threads)]
    # [login_through_form(x) for x in d]
    # # create a thread pool
    # with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    #     # run the function on each profile link
    #     executor.map(get_multiple_employee_data, d, employees, [employee_storage]*num_threads)
    # return employee_storage
    d = create_driver()
    login_through_form(d, from_homepage=True)
    employee_storage = Employees()
    for employee in employees[:5]:
        extract_employee_info(d, employee, employee_storage)
    return employee_storage

def check_for_captcha(driver: uc.Chrome) -> bool:
    if driver.find_elements(By.ID, 'CaptchaFrame'):
        logging.info('Captcha detected. Handle manually.')
        time.sleep(10)
        return True
    return False

def check_for_compliance(driver: uc.Chrome) -> bool:
    if (x:=driver.find_elements(By.CLASS_NAME, 'form__label')):
        if x.text.strip().startswith("I won't use tools that"):
            logging.info('Compliance detected. Handle manually.')
            time.sleep(10)
            return True
    return False
    


# if __name__ == '__main__':
#     t1 = time.perf_counter()
#     # create a driver for each thread
#     driver = create_driver()
#     # login from the home page
#     login_through_form(driver, from_homepage=True)
#     # get the list of public profiles
#     profiles = extract_company_employees(driver, total_employees=total_employees, return_profiles=True)
#     # close the driver
#     driver.quit()
#     # get the info for each profile
#     employees = get_all_employee_data(profiles)
#     # write the info to a csv
#     employees.save_as_csv('employees.csv')
#     t2 = time.perf_counter()
#     print(f'Total Runtine: {t2-t1:.2f} seconds')

if __name__ == '__main__':
    t1 = time.perf_counter()
    # get the list of profiles
    with open('profiles.txt', 'r') as f:
        profiles = [x.strip() for x in f.readlines()]
    parsed_profiles = get_all_employee_data(profiles)
    parsed_profiles.save_as_csv('employees.csv')
    t2 = time.perf_counter()
    print(f'Total Runtine: {t2-t1:.2f} seconds')