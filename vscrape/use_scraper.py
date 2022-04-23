from scraper import LinkedinScraper

'''
A wrapper around LinkedinScraper that only allows it to be called
with the `with` statement. This ensures that the driver always gets cleaned up.
'''
class UseScraper:
    def __enter__(self):
        self.scraper = LinkedinScraper()
        return self.scraper
    
    def __exit__(self, *args, **kwargs):
        self.scraper.driver.quit()

if __name__ == '__main__':
    with UseScraper() as scraper:
        scraper.login_from_home()
        scraper.extract_company_employees()
        scraper.employees.save_as_csv('test_run.csv')