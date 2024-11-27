ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import json
import os
import numpy as np
from skimage import io  # scikit-learn 包
import matplotlib.pyplot as plt
import pylab
import cv2


def get_tags(id: int) -> dict[str: int]:
    '''
    the method used now consume unnecessary computing source
    need rebulid the atchitechture to make it more efficient
    '''

    json_path = r'./Annotations/val.json'
    img_path = r'./Images/val/'
    with open(json_path) as annos:
        annotation_json = json.load(annos)
    image_name = annotation_json['images'][id]['file_name']
    category_dict = {category['id']: category['name'] for category in annotation_json['categories']}

    ...


def visualize(id: int, output_path) -> None:
    ...


if __name__ == '__main__':
    ...
    get_tags(2077)