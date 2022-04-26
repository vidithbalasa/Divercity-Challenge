from setuptools import setup

# get contents from readme
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name = 'leegs',
    version = '1.2.0',
    packages = ['leegs'],
    author = "Vidith Balasa",
    author_email = "vidithbalasa@gmail.com",
    description="A LinkedIn Profile Scraper",
    entry_points = {
        'console_scripts': [
            'leegs = leegs.__main__:main'
        ]
    },
    install_requires = [
        'selenium',
        'undetected-chromedriver',
        'requests',
        'pandas',
        'numpy',
        'tqdm',
    ],
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/vidithbalasa/Divercity-Challenge",
    python_requires=">=3.10"
)
