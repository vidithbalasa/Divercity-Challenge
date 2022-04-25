import os

'''
Settings for vscrape.
'''

# email = 'vbalasa@ucsc.edu'
# password = os.environ.get('LINKEDIN_PASSWORD')

# email = os.environ.get('LINKEDIN_EMAIL3')
# password = os.environ.get('LINKEDIN_PASSWORD3')

# email2 = os.environ.get('LINKEDIN_EMAIL6')
# password2 = os.environ.get('LINKEDIN_PASSWORD6')

emails = [os.environ.get(f'LINKEDIN_EMAIL{i}') for i in range(3, 7)]
passwords = [os.environ.get(f'LINKEDIN_PASSWORD{i}') for i in range(3, 7)]

total_employees = 100
company_url = 'https://www.linkedin.com/company/hubspot/'

num_threads = 4

DEBUG = True