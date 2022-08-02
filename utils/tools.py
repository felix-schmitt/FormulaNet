import cv2
import json

def resize_image(img_path, img_size, new_image):
    img = cv2.imread(str(img_path))
    h, w, _ = img.shape
    if img_size:
        ratio_old = h / w
        ratio_new = img_size['h'] / img_size['w']
        if ratio_old < ratio_new:
            h = int(ratio_old * img_size['w'])
            dh = img_size['h'] - h
            w = img_size['w']
            dw = 0
        else:
            w = int(1 / ratio_old * img_size['h'])
            dw = img_size['w'] - w
            h = img_size['h']
            dh = 0
        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
        img = cv2.copyMakeBorder(img, int(dh / 2), dh - int(dh / 2), int(dw / 2), dw - int(dw / 2),
                                 cv2.BORDER_CONSTANT, value=[255, 255, 255])
        cv2.imwrite(new_image, img)

def load_json(json_file):
    with open(json_file) as f:
        file = json.load(f)
        pages = [image['file_name'] for image in file['images']]
    f.close()
    return pages