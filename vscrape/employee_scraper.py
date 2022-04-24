import re, logging
import concurrent.futures
# default values
from settings import email, password, email2, password2, num_threads
# undetected chromedriver so my account stops getting locked
import undetected_chromedriver as uc
# selenium imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
# data storage
from data_storage import Employees
# funcs imports
from helper_funcs import check_for_captcha, check_for_compliance, login_through_form, create_driver

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
def get_all_employee_data(employees: list[str], total_employees:int=20) -> Employees:
    # split up employees into a num_threads lists for each thread
    employees = employees[:total_employees]
    employees = [employees[i::num_threads] for i in range(num_threads)]
    employee_storage = Employees()
    d = [create_driver(headless=True) for _ in range(num_threads-1)] + [create_driver(headless=False)]
    # 2 logins for now
    emails = [(email, password), (email2, password2)]
    # login to each driver with a different login
    [login_through_form(x, from_homepage=True, email=email, password=password) for (email, password), x in zip(emails, d)]
    # create a thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # run the function on each profile link
        executor.map(get_multiple_employee_data, d, employees, [employee_storage]*num_threads)
    return employee_storage
    # d = create_driver()
    # login_through_form(d, from_homepage=True)
    # employee_storage = Employees()
    # for employee in employees[:5]:
    #     extract_employee_info(d, employee, employee_storage)
    # return employee_storage

