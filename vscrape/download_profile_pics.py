import requests, sys, csv, logging, pathlib
import concurrent.futures

def download_profile_pics(file: str, path: str) -> None:
    '''
    Goes through given file an downloads all of the images. Then
    replaces profile_pic section with the image name.
    '''
    if not file.endswith('.csv'):
        print('Please specify a .csv file.')
        sys.exit(1)
    with open(file, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        # list of (link, name) for every employee w a profile pic
        pic_links = [(x[-1], f'{x[0]}_{i+1:03}') for i, x in enumerate(reader) if x]
    # download all the images concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(lambda p: download_profile_pic(*p, path), pic_links)
    print(f'Downloaded all profile pics into path: {path}')

def download_profile_pic(link: str, name: str, path: str) -> None:
    '''
    Downloads the profile pic from the given link.
    '''
    # make sure path exists, if not create it
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    # get the image
    r = requests.get(link)
    # save the image
    with open(f'{path}/{name}.jpg', 'wb') as f:
        f.write(r.content)
    logging.info(f"Downloaded profile pic for {name.split('_')[0]})")