import sys, argparse,logging
# import funcs
from .employee_scraper import get_employees_from_file
from .download_profile_pics import download_profile_pics

# basic logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # total_employees = 100
    match args.type:
        case 'company':
            # get the list of public profiles
            print('getting company info...')
        case 'employee':
            # get the info for each profile
            if args.file:
                print('getting info on each employee...')
                get_employees_from_file(args.file, output=args.output)
            elif args.profile_link:
                pass
            else:
                print('Please specify either a file or a profile link.')
                sys.exit(1)
    if args.download_profile_pics:
        download_profile_pics(args.output, args.profile_pic_dir)

if __name__ == '__main__':
    main()

'''CLI ARGUMENTS'''
# set up an argument parser that will parse the command line arguments
parser = argparse.ArgumentParser(description='Scrape LinkedIn for employee data.', formatter_class=argparse.RawTextHelpFormatter)
# basic arguments
parser.add_argument('type', choices=['company', 'employee'], help='''Company // go through company's LinkedIn, extract public employee profiles, then scrape info on each employee
\nEmployee // Scrape employee data for a single profile or a list of profiles''')
parser.add_argument('-o', '--output', type=str, default='data.csv', metavar='', help='filename to save the scraped data')
parser.add_argument('-d', '--download-profile-pics', action='store_true', help='download profile pics')
# args specific to the company scraper
company_args = parser.add_argument_group('company options')
company_args.add_argument('-n', '--num-employee', type=int, default=100, metavar='', help='total number of employees to scrape')
# args specific to the employee scraper
employee_args = parser.add_argument_group('employee options')
employee_args.add_argument('-f', '--file', type=str, default=None, metavar='', help='file containing the list of profiles to scrape')
employee_args.add_argument('-l', '--profile-link', type=str, default=None, metavar='', help='profile link to scrape')
# Arguments dependent on other arguments
dependent = parser.add_argument_group('dependent options')
dependent.add_argument('-p', '--profile-pic-dir', type=str, default='profile_pics', metavar='', help='directory to save profile pics')
args = parser.parse_args()