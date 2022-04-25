from setuptools import setup
setup(
    name = 'leegs',
    version = '1.1.0',
    packages = ['leegs'],
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
    ]
)