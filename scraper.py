import os, time
# undetected chromedriver cuz I got my account locked
import undetected_chromedriver as uc
# selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
# chrome options manager
from webdriver_manager.chrome import ChromeDriverManager
# personal imports
from data_storage import LinkedinEmployees

total_employees = 100

class LinkedinScraper():
    email = 'vbalasa@ucsc.edu'
    password = os.environ.get('LINKEDIN_PASSWORD')

    def __init__(self):
        # place to store employees
        self.employees = LinkedinEmployees()
        # opens the browser
        # self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver = uc.Chrome()
        self.driver.maximize_window()
        # go to the home page
        self.driver.get('https://www.linkedin.com/')
    
    def login_from_home(self) -> None:
        '''
        Logs in from the home page
        ---
        using a fake login because my actual one is through 
        apple, requiring 2-factor auth every time
        '''
        # type in email and passsword
        self.driver.find_element(By.ID, 'session_key').send_keys(self.email)
        self.driver.find_element(By.ID, 'session_password').send_keys(self.password)
        # find & click the sign-in button
        self.driver.find_element(By.CLASS_NAME, "sign-in-form__submit-button").click()
    
    def extract_company_employees(self, company_url: str='https://www.linkedin.com/company/hubspot/', get_all_public:bool=False) -> None:
        # go to the company page (the people section specifically)
        self.driver.get(company_url + 'people/')
        # wait for page to load
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'scaffold-finite-scroll')))
        '''
        Gets & stores all visible/public employees. Whenever it runs out of visible employees, it will scroll down
        to load more. Continues until it collects info on 100 employees.
        ---
        @param get_all_public: True if you want to get all public employees, even those w/o a profile pic
        '''
        # get the initial list of people on the page
        people_list = self.driver.find_elements(By.XPATH, '//div[@class="scaffold-finite-scroll__content"]/ul/li')
        # keep track of which person you're on
        counter = 0
        while len(self.employees) < total_employees:
            employee = people_list[counter]
            # add the employee to the list
            self._get_employee_info(employee, force=get_all_public)
            # update counter to start further in the list
            counter += 1
            if counter == len(people_list):
                # Scroll to bottom of page to load more employees
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                old_len = len(people_list)
                time.sleep(0.5)
                people_list = self.driver.find_elements(By.XPATH, '//div[@class="scaffold-finite-scroll__content"]/ul/li')
                if old_len < len(people_list):
                    continue
                # check for new people 5 times before giving up (accounts for varying loading times w/o wasting time)
                loop_count = 0
                while loop_count < 5 and old_len == len(people_list):
                    loop_count += 1
                    time.sleep(0.5)
                    # same line as above, could outsource into a function if needed
                    people_list = self.driver.find_elements(By.XPATH, '//div[@class="scaffold-finite-scroll__content"]/ul/li')
                # break out of the loop if there are no more people to load
                if old_len == len(people_list):
                    break
        
    def _get_employee_info(self, employee, force:bool=False) -> None:
        '''
        Extracts info from an employee's profile
        ---
        @param employee: the employee's profile element
        @param get_info: True if you want it to return the info, Flase if you want it to store it
        @param force: Force it to get the info even without a profile pic
        '''
        # get the name & label for each employee
        name, label, *_ = employee.text.split('\n')
        # skip if their profile is private
        if name.startswith('LinkedIn'):
            return
        if employee.find_elements(By.CLASS_NAME, 'ghost-person') and not force:
            return
        # open their profile in a new tab
        ActionChains(self.driver).key_down(Keys.COMMAND).click(employee).perform()
        # go to the second tab
        self.driver.switch_to.window(self.driver.window_handles[-1])
        # wait for page to load
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'pb2')))
        # get location
        location = self.driver.find_element(By.CLASS_NAME, 'pb2').text
        # get profile pic
        profile_pic = self.driver.find_elements(By.CLASS_NAME, 'pv-top-card-profile-picture__image')
        if not profile_pic:
            return
        profile_pic = profile_pic[0].get_attribute('src')
        # close the tab to back to the original tab
        if len(self.driver.window_handles) > 1:
            self.driver.close()
        # switch to original window so selenium can continue
        self.driver.switch_to.window(self.driver.window_handles[0])
        # add info to employees list
        self.employees.add_employee(*name.split(maxsplit=1), location=location, label=label, profile_pic=profile_pic)
        # give it a second to process
        time.sleep(0.1)