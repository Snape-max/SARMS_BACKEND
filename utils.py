import hashlib
import os
from pathlib import Path
import cv2
import pickle as pkl

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
CATEGORIES = {
    0: 'ship',
    1: 'aircraft',
    2: 'car',
    3: 'tank',
    4: 'bridge',
    5: 'harbor',
}

def rgb(r,g,b):
    return b, g, r

COLORS = {
    0: rgb(255, 157, 226),
    1: rgb(140, 130, 252),
    2: rgb(182, 147, 254),
    3: rgb(126, 255, 219),
    4: rgb(255, 211, 182),
    5: rgb(245, 113, 112)
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_md5_from_image(image):
    """从cv2图像对象计算MD5哈希值"""
    hash_md5 = hashlib.md5()
    # 将图像编码为JPEG格式（或任何其他格式），以便可以计算哈希值
    is_success, im_buf_arr = cv2.imencode(".jpg", image)
    if not is_success:
        raise ValueError("Failed to encode image.")
    byte_im = im_buf_arr.tobytes()
    hash_md5.update(byte_im)
    return hash_md5.hexdigest()


class SarTools:
    def __init__(self, label_pkl: str):
        self.label_pkl = label_pkl
        self.label_data = self.__init_data()


    def __init_data(self):
        if not os.path.exists(self.label_pkl):
            raise FileNotFoundError(self.label_pkl)
        fb = open(self.label_pkl, 'rb')
        return pkl.load(fb)

    def get_tags(self, image_name: str) -> dict | None:
        if image_name in self.label_data.keys():
            return self.label_data[image_name]["tags"]
        return None

    def draw_box(self, image_name: str, image_path: str, save_path: str):
        image = cv2.imread(image_path)
        id_boxes: dict = self.label_data[image_name]["box"]
        for tid, boxes in id_boxes.items():
            for box in boxes:
                x, y, w, h = [int(i) for i in box]
                cv2.rectangle(image, (x, y), (x+w, y+h), COLORS[tid], 2)
        # 获取处理后图像的MD5哈希值
        md5_hash = get_md5_from_image(image)

        # 创建保存路径的目录（如果它不存在）
        Path(save_path).mkdir(parents=True, exist_ok=True)

        # 构建完整的目标文件路径，包括带有md5哈值的新文件名和扩展名
        target_file_path = Path(save_path) / f"{md5_hash}.jpg"  # 假设我们使用的是JPEG格式

        # 保存图像
        cv2.imwrite(str(target_file_path), image)
        return md5_hash, f"{save_path}/{md5_hash}.jpg"





if __name__ == '__main__':
    tools = SarTools('test/label.pkl')
    print(tools.get_tags('0000005.jpg'))
    tools.draw_box('0000005.jpg', 'test/0000005.jpg', 'test/label.png')