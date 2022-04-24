import re, time, logging
from typing import Optional
# default values
from settings import total_employees, company_url
# undetected chromedriver so my account stops getting locked
import undetected_chromedriver as uc
# selenium imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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