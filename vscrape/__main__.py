import sys, argparse, logging, os
# import funcs
from .employee_scraper import get_all_employee_data, get_employees_from_file, extract_employee_info
from .download_profile_pics import download_profile_pics
from .company_scraper import extract_company_employees
from .helper_funcs import create_driver, login_through_form, write_genders_to_csv
from .data_storage import Employees
from .gender_detection import detect_genders_from_dir

def run_full_bot() -> None:
    '''
    Runs the full process per the project outlines
    '''
    # create a driver
    driver = create_driver()
    # login
    login_through_form(driver, from_homepage=True)
    # get the list of public profiles
    print('getting list of employees...')
    # call the function to get the list of public profiles
    profiles = extract_company_employees(driver, total_employees=args.tot_employee, return_profiles=True)
    driver.quit()
    # get the employee data from the profile links
    print('getting info on each employee...')
    employees = get_all_employee_data(profiles)
    employees.save_as_csv(args.output)

    # download profile pics
    if not args.no_downloads:
        download_profile_pics(args.output, args.pictures_dir)
        # Face analysis w deepface
        if args.face_detection:
            analysis = detect_genders_from_dir(args.pictures_dir)
            write_genders_to_csv(args.output, analysis)

def main():
    # basic logging settings
    logging.basicConfig(level=logging.INFO if args.debug else logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')

    # if no downloads is turned off & pictures dir exists & it's not empty then tell the user to empty it
    if ( not args.no_downloads ) and os.path.isdir(args.pictures_dir) and ( not os.path.listdir(args.pictures_dir) ):
        print('Please ensure the specified "--pictures-dir" directory is empty.')
        sys.exit(1)

    match args.type:
        case 'hubspot':
            # get the list of public profiles
            # print('getting company info...')
            # run the full thing
            run_full_bot()
        case 'employee':
            # get the info for each profile
            if args.file:
                print('getting info on each employee...')
                get_employees_from_file(args.file, output=args.output)
                # download their profile pics
                if not args.no_downloads:
                    download_profile_pics(args.output, args.pictures_dir)
                    if args.face_detection:
                        genders = detect_genders_from_dir(args.pictures_dir)
                        write_genders_to_csv(args.output, genders)
            elif args.profile_link:
                driver = create_driver(headless=True)
                print('logging in...')
                login_through_form(driver, from_homepage=True)
                employees = Employees()
                extract_employee_info(driver, args.profile_link, employees)
                if not args.no_downloads:
                    download_profile_pics(args.output, args.pictures_dir)
                    if args.face_detection:
                        genders = detect_genders_from_dir(args.pictures_dir)
                print(employees)
                if genders: print(f'Gender: {genders[1]}')
            else:
                print('Please specify either a file or a profile link.')
                sys.exit(1)

if __name__ == '__main__':
    main()

'''CLI ARGUMENTS'''
# set up an argument parser that will parse the command line arguments
parser = argparse.ArgumentParser(description='Scrape LinkedIn for employee data.', formatter_class=argparse.RawTextHelpFormatter)
# basic arguments
parser.add_argument('type', choices=['hubspot', 'employee'], help='''Hubspot // go through hubspot's LinkedIn, extract public employee profiles, then scrape info on each employee
\nEmployee // Scrape employee data for a single profile or a list of profiles''')
parser.add_argument('-o', '--output', type=str, default='data.csv', metavar='', help='filename to save the scraped data')
## download pics argument thats default true and can be turned off
parser.add_argument('-n', '--no-downloads', action='store_true', help='download profile pics')
parser.add_argument('-p', '--pictures-dir', type=str, default='profile_pics', metavar='', help='directory to save profile pics (required unless you set --no-downloads)')
parser.add_argument('-a', '--face-detection', action='store_true', help='analyze faces of downloaded profile pics')
parser.add_argument('--debug', action='store_true', help='enable logging', default=False)
# args specific to the company scraper
company_args = parser.add_argument_group('company options')
company_args.add_argument('-t', '--tot-employee', type=int, default=100, metavar='', help='total number of employees to scrape')
# args specific to the employee scraper
employee_args = parser.add_argument_group('employee options')
employee_args.add_argument('-f', '--file', type=str, default=None, metavar='', help='file containing the list of profiles to scrape')
employee_args.add_argument('-l', '--profile-link', type=str, default=None, metavar='', help='profile link to scrape')
# args specific to the profile pic
args = parser.parse_args()