import os

'''
Settings for vscrape.
'''

# email = 'vbalasa@ucsc.edu'
# password = os.environ.get('LINKEDIN_PASSWORD')

email = os.environ.get('LINKEDIN_EMAIL5')
password = os.environ.get('LINKEDIN_PASSWORD5')

email2 = os.environ.get('LINKEDIN_EMAIL6')
password2 = os.environ.get('LINKEDIN_PASSWORD6')

total_employees = 100
company_url = 'https://www.linkedin.com/company/hubspot/'

num_threads = 2