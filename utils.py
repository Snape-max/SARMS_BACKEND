import json
import os
import cv2
from collections import defaultdict
import itertools

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def _isArrayLike(obj):
    return hasattr(obj, '__iter__') and hasattr(obj, '__len__')

class sartools:
    def __init__(self, annotation_file=None, image_folder=None):
        """
        intializa the sartools for sarms
        :param annotation_file (str): location of annotation file
        :param image_folder (str): location to the folder that hosts images.
        :return:
        """
        # load dataset
        self.dataset,self.anns,self.cats,self.imgs = dict(),dict(),dict(),dict()
        self.imgToAnns, self.catToImgs = defaultdict(list), defaultdict(list)
        self.image_folder = image_folder
        if not annotation_file == None:
            with open(annotation_file, 'r') as f:
                dataset = json.load(f)
            self.dataset = dataset
            self.createIndex()
        return
    def createIndex(self):
        # create index
        anns, cats, imgs = {}, {}, {}
        imgToAnns,catToImgs = defaultdict(list),defaultdict(list)
        if 'annotations' in self.dataset:
            for ann in self.dataset['annotations']:
                imgToAnns[ann['image_id']].append(ann)
                anns[ann['id']] = ann

        if 'images' in self.dataset:
            for img in self.dataset['images']:
                imgs[img['id']] = img

        if 'categories' in self.dataset:
            for cat in self.dataset['categories']:
                cats[cat['id']] = cat

        if 'annotations' in self.dataset and 'categories' in self.dataset:
            for ann in self.dataset['annotations']:
                catToImgs[ann['category_id']].append(ann['image_id'])

        # create class members
        self.anns = anns
        self.imgToAnns = imgToAnns
        self.catToImgs = catToImgs
        self.imgs = imgs
        self.cats = cats
        return
    def getAnns(self, imgIds=[], catIds=[]):
        """
        Get ann ids that satisfy given filter conditions. default skips that filter
        :param imgIds  (int array)     : get anns for given imgs
               catIds  (int array)     : get anns for given cats
        :return: anns (dict)
        """
        imgIds = imgIds if _isArrayLike(imgIds) else [imgIds]
        catIds = catIds if _isArrayLike(catIds) else [catIds]

        if len(imgIds) == len(catIds) == 0:
            anns = self.dataset['annotations']
        else:
            if not len(imgIds) == 0:
                lists = [self.imgToAnns[imgId] for imgId in imgIds if imgId in self.imgToAnns]
                anns = list(itertools.chain.from_iterable(lists))
            else:
                anns = self.dataset['annotations']
            anns = anns if len(catIds)  == 0 else [ann for ann in anns if ann['category_id'] in catIds]
        # ids = [ann['id'] for ann in anns]
        return anns

    def getTags(self, imgIds=[], catIds=[]) -> dict[str: int]:
        queryanns=self.getAnns(imgIds, catIds)
        imgIds = imgIds if _isArrayLike(imgIds) else [imgIds]
        temp={i:0 for i in range(6)}
        dic=defaultdict(int)
        for id in imgIds:
            dic[id]=temp
        for ann in queryanns:
            imid=ann['image_id']
            catid=ann['category_id']
            dic[imid][catid]+=1
        return dic

    def visualize(self, output_path,imgIds=[], catIds=[]):
        """
        display the image and its annotations
        :param imgIds (int array)     : get image ids for given ids
        :return:
        """
        anns=self.getAnns(imgIds, catIds)
        category_dict = {category['id']: category['name'] for category in self.dataset['categories']}
        for id in imgIds:
            image_name=self.imgs[id]['file_name']
            image_path=os.path.join(self.image_folder,image_name)
            image = cv2.imread(image_path, 1)
            for ann in anns:
                if ann['image_id']==id:
                    category_id=ann['category_id']
                    category_name=category_dict[category_id]
                    x,y,w,h=ann['bbox']
                    cv2.rectangle(image, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)
                    cv2.putText(image, category_name, (int(x), int(y-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, ())

            cv2.imwrite(output_path+image_name+'labeled.jpg',image)

        return

if __name__ == "__main__":
    # follow is how to use sartools

    dataType='val'   # option: val test train
    dataDir='../Images/{}/'.format(dataType)
    annFile='../Annotations/{}.json'.format(dataType)

    # initialize
    sartool=sartools(annFile,dataDir)

    # three function
    test=sartool.getAnns(2077)
    dic=sartool.getTags([2077,2078])
    sartool.visualize('./test./',[2077])