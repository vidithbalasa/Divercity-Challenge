import os, time
import undetected_chromedriver.v2 as uc
# selenium imports
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# other imports
from data_storage import LinkedinEmployees, LinkedinProfile

class LinkedinScraper():
    email = 'vbalasa@ucsc.edu'
    password = os.environ.get('LINKEDIN_PASSWORD')

    def __init__(self):
        # place to store employees
        self.employees = LinkedinEmployees()
        # opens the browser
        self.driver = self._driver_setup() # automatic cleanup w selenium
        # go to the home page
        self.driver.get('https://www.linkedin.com/')
    
    def login_from_home(self) -> None:
        '''
        using a fake login because my actual one is through 
        apple, requiring 2-factor auth every time
        '''
        # type in email and passsword
        self.driver.find_element(By.ID, 'session_key').send_keys(self.email)
        self.driver.find_element(By.ID, 'session_password').send_keys(self.password)
        # find & click the sign-in button
        submit_btn = self.driver.find_element(By.CLASS_NAME, "sign-in-form__submit-button").click()
    
    def extract_company_employees(self, company_url: str='https://www.linkedin.com/company/hubspot/') -> None:
        # go to the company page (the people section specifically)
        self.driver.get(company_url + 'people/')
        # wait for page to load
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'scaffold-finite-scroll')))
        '''
        Gets & stores all visible/public employees. Whenever it runs out of visible employees, it will scroll down
        to load more. Continues until it collects info on 100 employees.
        '''
        # get the initial list of people on the page
        people_list = self.driver.find_elements(By.XPATH, '//div[@class="scaffold-finite-scroll__content"]/ul/li')
        # keep track of which person you're on
        counter = 0
        while len(self.employees) < 10:
            employee = people_list[counter]
            # get the name & label for each employee
            name, label, *_ = employee.text.split('\n')
            # skip if their profile is private
            if not name.startswith('LinkedIn'):
                # open their profile in a new tab
                ActionChains(self.driver).key_down(Keys.COMMAND).click(employee).perform()
                # go to the second tab
                self.driver.switch_to.window(self.driver.window_handles[-1])
                # wait for page to load
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'pb2')))
                # get location
                location = self.driver.find_element(By.CLASS_NAME, 'pb2').text
                # get profile pic
                try:
                    profile_pic = self.driver.find_element(By.CLASS_NAME, 'pv-top-card-profile-picture__image').get_attribute('src')
                except:
                    # dont care about the exception, this just lets us know that there is no profile pic
                    profile_pic = ''
                # close the tab to back to the original tab
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                # switch to original window so selenium can continue
                self.driver.switch_to.window(self.driver.window_handles[0])
                # add info to employees
                if profile_pic:
                    self.employees.add_employee(*name.split(maxsplit=1), location=location, label=label, profile_pic=profile_pic)
                # update counter to start further in the list
            counter += 1
            if counter == len(people_list):
                # Scroll to bottom of page to load more employees
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                old_len = len(people_list)
                # check for new people 5 times before giving up
                loop_count = 0
                while loop_count < 5 and old_len == len(people_list):
                    loop_count += 1
                    time.sleep(0.5)
                    # same line as above, could outsource into a function if needed
                    people_list = self.driver.find_elements(By.XPATH, '//div[@class="scaffold-finite-scroll__content"]/ul/li')
            # print(self.employees)
    
    def _driver_setup(self) -> uc.Chrome:
        # Configure basic chrome options 
        options = uc.ChromeOptions()
        # to turn off popups by saving the cookies
        options.add_argument('--no-first-run --no-service-autorun --password-store=none')
        # Getting rid of the password manager (aesthetic purposes tbh, but it's not necessary)
        options.add_argument('--password_manager_enabled=false')
        # Creates and returns the configured driver
        driver = uc.Chrome(options=options)
        driver.maximize_window()
        return driver

if __name__ == '__main__':
    scraper = LinkedinScraper()
    scraper.login_from_home()
    scraper.extract_company_employees()
    scraper.employees.save_as_csv('test_run1.csv')