import cv2

def is_grayscale(src):
    # 縮小する
    size = 160
    img = cv2.resize(src, (size, size))
    
    # 中心からクリップする
    clip_to = 100
    x, y = size // 2, size // 2
    img = img[y-clip_to//2:y+clip_to//2, x-clip_to//2:x+clip_to//2]
        
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    H_STEP = 32
    x = round(180 / H_STEP)
    hsv[:, :, 0] = np.array(np.round(np.round(hsv[:, :, 0] / x)  * x) , dtype=np.uint8)

    S_STEP = 4
    x = round(255 / S_STEP)
    hsv[:, :, 1] = np.array(np.round(np.round(hsv[:, :, 1] / x) * x) , dtype=np.uint8)
    hsv[:, :, 2] = 255

    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    img = Image.fromarray(img[:, :, ::-1])
    img = img.filter(ImageFilter.ModeFilter(14))
    img = np.array(img, dtype=np.uint8)[:, :, ::-1]

    # 色を数える
    colors = np.reshape(img, [img.shape[0] * img.shape[1], 3])
    colors = np.array(colors, dtype=np.uint8)
    colors = np.unique(colors, axis=0)
    
    color_counts = []
    for c in colors:
        color_counts.append(np.count_nonzero((img - c).sum(2) == 0))
    
    colors = [i for i in color_counts if i >= 20]
    return len(colors) <= 5
