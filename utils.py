import json
import os
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

def visualize(id: int, output_path) -> None:
    ...
    json_path = r'../Annotations/val.json'
    img_path = r'../Images/val/'
    with open(json_path) as annos:
        annotation_json = json.load(annos)
    image_name = annotation_json['images'][id]['file_name']
    image_path = os.path.join(img_path, str(image_name).zfill(5))  # 拼接图像路径
    image = cv2.imread(image_path, 1)  # 保持原始格式的方式读取图像
    category_dict = {category['id']: category['name'] for category in annotation_json['categories']}
    for annotation in annotation_json['annotations']:
        if annotation['image_id'] == id:
            x, y, w, h = annotation['bbox']  # 读取边框
            category_id = annotation['category_id']
            category_name = category_dict.get(category_id, 'Unknown')  # 获取类别名称
            image = cv2.rectangle(image, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)  # 绿色矩形框
            image = cv2.putText(image, category_name, (int(x), int(y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)  # 在矩形框上方添加类别名称
    cv2.imwrite(output_path, image)
    return None