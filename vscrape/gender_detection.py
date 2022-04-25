import os, time, sys, logging
from tqdm import tqdm

def detect_gender(file: str, DeepFace) -> str:
    '''
    Detect gender of person in image using deepface
    '''
    res = DeepFace.analyze(file, actions = ['gender'], detector_backend='retinaface', enforce_detection=False)
    # path/to/file.jpg -> file.jpg
    filename = os.path.split(file)[1]
    # name_position.jpg -> name_position -> position
    return res['gender'], filename.split('.')[0].split('_')[1]

def detect_genders_from_dir(dir: str) -> dict[str]:
    '''
    Detect gender for every image in a directory
    '''
    if not os.path.isdir(dir):
        print(f'Confirm that {dir} exists')
        sys.exit(1)
    genders = dict()
    from deepface import DeepFace # internal import to avoid lag
    for path in tqdm(os.listdir(dir), desc='Analyzing Genders'):
        gender, position = detect_gender(f'{dir}/{path}', DeepFace)
        genders[int(position)] = gender
    logging.info(f'{"="*10}ASSIGNED {len(genders)} GENDERS{"="*10}') # lmao
    return genders



if __name__ == '__main__':
    t1 = time.perf_counter()
    detect_genders_from_dir('profile_pics')
    t2 = time.perf_counter()
    print(f'Total Runtime :: {t2-t1:.2f}')
