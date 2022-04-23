import sys
from use_scraper import UseScraper

def main():
    args = sys.argv[1:]
    get_all = False
    # total_employees = 100
    match args[0]:
        case '--get-all':
            get_all = True
        
    
    with UseScraper() as scraper:
        scraper.login_from_home()
        scraper.extract_company_employees(get_all_public=get_all)
        scraper.employees.save_as_csv('test_run.csv')

if __name__ == '__main__':
    main()