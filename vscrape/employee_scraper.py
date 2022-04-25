import re, logging, sys
import concurrent.futures
# default values
from .settings import emails, passwords, num_threads
# undetected chromedriver so my account stops getting locked
import undetected_chromedriver as uc
# selenium imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
# data storage
from .data_storage import Employees
# funcs imports
from .helper_funcs import check_for_captcha, check_for_compliance, login_through_form, create_driver
# cli imports
from tqdm import tqdm

# concurrent function that runs extract_employee information on multiple threads
def get_all_employee_data(employees: list[str]) -> Employees:
    # split up employees into `num_threads` lists to evenly distribute workload across threads
    employees = [employees[i::num_threads] for i in range(num_threads)]
    # create global employees object for all threads to access
    employee_storage = Employees()
    # create a driver for each thread (w one non-headless driver)
    drivers = [create_driver(headless=False)] + [create_driver(headless=True) for _ in range(num_threads-1)]
    # login to each driver with a different login
    [login_through_form(driver, from_homepage=True, email=email, password=password) for email, password, driver in zip(emails, passwords, drivers)]
    # object to update the loading bar for the cli
    loader = tqdm(total=sum([len(x) for x in employees]), desc='Crawling Profiles')
    # create a thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # lambda takes in a driver, employees, & storage -- calls extract_employee_info for each employee in list
            # (d,i,s,l) == (driver, profile_link, employee_storage, loader)
        executor.map(lambda d,e,s,l: [extract_employee_info(d,p,s,l) for p in e], drivers, employees, [employee_storage]*num_threads, [loader]*num_threads)
    return employee_storage

# get the info for a single profile
def extract_employee_info(driver: uc.Chrome, profile_link:str, employees: Employees, loader: tqdm) -> None:
    driver.get(profile_link)
    # wait for the profile to load
    check_for_captcha(driver)
    check_for_compliance(driver)
    # if theres a sign in form prompt, press the sign in button and run the login function
    if driver.find_elements(By.CLASS_NAME, 'join-form'):
        driver.find_element(By.CLASS_NAME, 'authwall-join-form__form-toggle--bottom').click()
        login_through_form(driver)
        driver.get(profile_link)
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
    # replace commas in last name
    last_name = last_name.replace(',', ';')
    # get label
    label = box.find_element(By.CLASS_NAME, 'text-body-medium').text
    # replace commas in label
    label = label.replace(',', ';')
    # get location
    location = box.find_element(By.CLASS_NAME, 'pb2').text
    # location sometimes has 'Contact Info' at the end of it and we wanna remove that
    location = location.split('Contact info')[0]
    # replace commas from location
    location = location.replace(',', ';')
    # get profile picture
    # check that they don't have a ghost profile pic
    if box.find_elements(By.CLASS_NAME, 'ghost-person'):
        profile_pic = ''
    else:
        profile_pic = box.find_element(By.CLASS_NAME, 'pv-top-card-profile-picture__image').get_attribute('src')
    # if profile_pic:
    #     download_profile_pic(profile_pic, f'{hash(first_name)}.jpg')
    # store all this info in the employees object
    employees.add_employee(first_name, last_name, label=label, location=location, profile_pic=profile_pic)
    logging.info(f'{first_name} {last_name} added to employees: {employees[0].label}')
    # update the loading bar
    loader.update(1)

def get_employees_from_file(file:str, /, *, output:str) -> None:
    '''
    Scrape LinkedIn profiles from a file.
    '''
    # get the list of public profiles
    logging.info('getting employee info...')
    if not file.endswith('.txt'):
        logging.error('Please specify a .txt file.')
        sys.exit(1)
    with open (file, 'r') as f:
        employees = [x.strip() for x in f.readlines()]
    company_employees = get_all_employee_data(employees)
    # write all the info to a csv file
    company_employees.save_as_csv(output)