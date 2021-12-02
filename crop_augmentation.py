

import os
import cv2 as cv 
import csv
import random
import argparse
parser = argparse.ArgumentParser(description='Simple training script for training a RetinaNet network.')
parser.add_argument('--csv_train', help='Path to file containing training annotations (see readme)')
parser = parser.parse_args()

def crop_image(xmin, ymin, w = 224, h = 224):
    xmax = xmin + w
    ymax = ymin + h
    return img[xmin:xmax, ymin:ymax]

def load_images(annots_file):
    # load image information into list 
    imagePaths = []
    bbox_coords = []
    with open(annots_file, newline = '') as file:
        pathreader = csv.reader(file, delimiter=',')
        for row in pathreader:
            imagePath = row[0]
            bbox_coord = [row[1], row[2], row[3], row[4]]
            imagePaths.append(imagePath)
            bbox_coords.append(bbox_coord)
    return imagePaths, bbox_coords

crop_w = 224
crop_h = 224
n_crops = 6

imagePaths, bbox_coords = load_images(parser.csv_train)

# draw image and bounding box
i = -1
for sample in imagePaths:
    i += 1
    img = cv.imread(sample)
    
    h, w = img.shape[:-1]
    
    # bounding box coords
    startX = int(float(bbox_coords[i][0]))
    startY = int(float(bbox_coords[i][1]))
    endX = int(float(bbox_coords[i][2]))
    endY = int(float(bbox_coords[i][3]))
    
    # don't accept crops that extend beyond image size
    max_possible_xmin = w - crop_w
    max_possible_ymin = h - crop_h

    for crop in range(n_crops):
        
        # record original image
        visual = img.copy()

        # crop image
        crop_name = "crop_" + str(crop)
        crop_xmin = random.randint(0, max_possible_xmin)
        crop_ymin = random.randint(0, max_possible_ymin)
        crop_xmax = crop_xmin + crop_w
        crop_ymax = crop_ymin + crop_h
        cropped_img = visual[crop_ymin:crop_ymax, crop_xmin:crop_xmax]
        #print(crop_name, cropped_area.shape[:-1], 'relative coords', crop_xmin, crop_ymin, crop_xmax, crop_ymax)

        # draw bbox in red and crop frames in blue on original image
        # cv.rectangle(visual, (startX, startY), (endX, endY), (0, 0, 255), 2)
        # cv.rectangle(visual, (crop_xmin, crop_ymin), (crop_xmax, crop_ymax), (255, 0, 0), 2)
        cv.imshow("original", visual)


        # compute new relative bbox coordinates
        if (startX > crop_xmin) & (startX < crop_xmax): 
            startX_crop = startX - crop_xmin
            if endX < crop_xmax:
                endX_crop = endX - crop_xmin
            else:
                endX_crop = crop_xmax
        elif (endX < crop_xmax) & (endX > crop_xmin):
            startX_crop = crop_xmin
            endX_crop = endX - crop_xmin
        else:
            startX_crop = None
            endX_crop = None

        if (startY > crop_ymin) & (startY < crop_ymax):
            startY_crop = startY - crop_ymin
            if endY < crop_ymax:
                endY_crop = endY - crop_ymin
            else:
                endY_crop = crop_ymax
        elif (endY < crop_ymax) & (endY > crop_ymin):
            startY_crop = crop_ymin
            endY_crop = endY - crop_ymin
        else:
            startY_crop = None 
            endY_crop = None 
        startX_crop = startX - crop_xmin
        endX_crop = endX - crop_xmin
        startY_crop = startY - crop_ymin
        endY_crop = endY - crop_ymin

        # show croppped image with new bbox coordinates
        cv.rectangle(cropped_img, (startX_crop, startY_crop), (endX_crop, endY_crop), (0, 0, 255), 2)
        cv.imshow("cropped", cropped_img)

        print('bounding box absolute coords', startX, startY, endX, endY)

        k = cv.waitKey(0) & 0xFF
        cv.destroyWindow(crop_name)

    k = cv.waitKey(0) & 0xFF
    if k == 27: 
        cv.destroyAllWindows()
        break

    # # compute array of valid upper-left corner points
    # max_x = int(float(w)) - 224
    # max_y = int(float(h)) + 224
    # text =str(max_x) + ', ' + str(max_y)
    # cv.putText(visual, "max y", (0, max_y), cv.FONT_HERSHEY_PLAIN, 0.65, (0, 0, 255), 2)
    # cv.putText(visual, "max_x", (max_x, 0), cv.FONT_HERSHEY_PLAIN, 0.65, (0, 0, 255), 2)
    # cv.imshow("test", visual)
    # cv.waitKey(0)
    # k = cv.waitKey(0) & 0xFF
    # if k == 27:
    #         cv.destroyAllWindows()
    #         break
    # show image 
