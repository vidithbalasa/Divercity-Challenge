import os, time
import undetected_chromedriver.v2 as uc
# selenium imports
from selenium.webdriver.common.by import By
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
        # find the email and password fields
        email_field = self.driver.find_element(By.ID, 'session_key')
        password_field = self.driver.find_element(By.ID, 'session_password')
        # enter the email and password
        email_field.send_keys(self.email)
        password_field.send_keys(self.password)
        # find & click the login button
        submit_btn = self.driver.find_element(By.CLASS_NAME, "sign-in-form__submit-button")
        submit_btn.click()
    
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
        # keep track of original tab
        original_tab = self.driver.current_window_handle
        for _ in range(5):
            unseen_employees = people_list[counter:]
            employee = unseen_employees[counter]
            # get the name of the employee, only public employees have this class name
            try:
                name = employee.find_element(By.CLASS_NAME, 'org-people-profile-card__profile-title').text
            except:
                # we don't care about the exception, this just lets us know that we're on a private profile
                print('nope')
                counter += 1
                continue
            # click on their profile for location & profile pic
            employee.click()
            # wait for page to load
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'pb2')))
            # get location
            location = self.driver.find_element(By.CLASS_NAME, 'pb2').text
            # get profile pic
            profile_pic = self.driver.find_element(By.CLASS_NAME, 'pv-top-card-profile-picture__image').get_attribute('src')
            print(f'{name=} - {location=} - {profile_pic=}')
            # go back to the page of all the employees
            self.driver.back()
            # update counter to start further in the list
            counter += 1
            if counter == len(unseen_employees):
                # Scroll to bottom of page to load more employees
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                # same line as above, could outsource into a function if needed
                people_list = self.driver.find_elements(By.XPATH, '//div[@class="scaffold-finite-scroll__content"]/ul/li')
    
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