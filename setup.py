from setuptools import setup
setup(
    name = 'vscrape',
    version = '0.1.0',
    packages = ['vscrape'],
    entry_points = {
        'console_scripts': [
            'vscrape = vscrape.__main__:main'
        ]
    })