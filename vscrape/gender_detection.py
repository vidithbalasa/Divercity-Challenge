import os, time, sys, csv
import concurrent.futures
import pandas as pd
import numpy as np

def detect_gender(file: str, DeepFace) -> str:
    '''
    Detect gender of person in image using deepface
    '''
    res = DeepFace.analyze(file, actions = ['gender'], detector_backend='retinaface')
    # path/to/file.jpg -> file.jpg
    filename = os.path.split(file)[1]
    # name_position.jpg -> name_position -> position
    return res['gender'], filename.split('.')[0].split('_')[1]

def detect_genders_from_dir(dir: str) -> dict[str]:
    if not os.path.isdir(dir):
        print(f'Confirm that {dir} exists')
        sys.exit(1)
    print(f'{"="*5}Running Image Detection for Face Analaysis...{"="*5}')
    # images = [f'{dir}/{f}' for f in os.listdir(dir)]
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = executor.map(detect_gender, images)
    #     for gender, position in results:
    #         genders[position] = gender
    genders = dict()
    from deepface import DeepFace # internal import to avoid lag
    for path in os.listdir(dir):
        gender, position = detect_gender(f'{dir}/{path}', DeepFace)
        genders[int(position)] = gender
    print(f'{"="*10}ASSIGNED {len(genders)} GENDERS{"="*10}')
    return genders



if __name__ == '__main__':
    t1 = time.perf_counter()
    detect_genders_from_dir('profile_pics')
    t2 = time.perf_counter()
    print(f'Total Runtime :: {t2-t1:.2f}')
