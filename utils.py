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

    json_path = r'../Annotations/val.json'
    img_path = r'../Images/val/'
    with open(json_path) as annos:
        annotation_json = json.load(annos)
    image_name = annotation_json['images'][id]['file_name']
    category_dict = {category['id']: category['name'] for category in annotation_json['categories']}
    dic = {i:0 for i in range(5)}
    for ann in annotation_json['annotations']:
        if ann['image_id'] == id:
            category_id = ann['category_id']
            dic[category_id]+=1
    return dic
    ...


def visualize(id: int, output_path) -> None:
    ...
    json_path = r'../Annotations/val.json'
    img_path = r'../Images/val/'
    with open(json_path) as annos:
        annotation_json = json.load(annos)
    image_name = annotation_json['images'][id]['file_name']
    image_path = os.path.join(img_path, str(image_name).zfill(5))  # 拼接图像路径
    image = cv2.imread(image_path, 1)  # 保持原始格式的方式读取图像
    num_bbox = 0  # 统计一幅图片中bbox的数量

    # 创建一个字典来存储类别id和类别名称的对应关系
    category_dict = {category['id']: category['name'] for category in annotation_json['categories']}

    for annotation in annotation_json['annotations']:
        if annotation['image_id'] == id:
            num_bbox += 1
            x, y, w, h = annotation['bbox']  # 读取边框
            category_id = annotation['category_id']
            category_name = category_dict.get(category_id, 'Unknown')  # 获取类别名称
            image = cv2.rectangle(image, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)  # 绿色矩形框
            image = cv2.putText(image, category_name, (int(x), int(y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)  # 在矩形框上方添加类别名称

    print('The num_bbox of the display image is:', num_bbox)

    # 显示方式2：用cv2.imshow()显示
    cv2.namedWindow(image_name, 0)  # 创建窗口
    cv2.resizeWindow(image_name, 500, 500)  # 创建500*500的窗口
    cv2.imshow(image_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()  # 关闭所有窗口

if __name__ == '__main__':
    ...
    dic=get_tags(2077)
    print(dic)
    visualize(2077,'./test./')