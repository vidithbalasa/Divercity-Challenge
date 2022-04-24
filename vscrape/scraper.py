# imports funcs
import time, logging
from company_scraper import extract_company_employees
from employee_scraper import get_all_employee_data
from helper_funcs import login_through_form, create_driver

# basic logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    parsed_profiles = get_all_employee_data(profiles, 20)
    parsed_profiles.save_as_csv('employees.csv')
    t2 = time.perf_counter()
    print(f'Total Runtine: {t2-t1:.2f} seconds')