import torch
import numpy as np
import time
import os
import csv
import cv2
import argparse

assert torch.__version__.split('.')[0] == '1'

print('CUDA available: {}'.format(torch.cuda.is_available()))

def load_classes(csv_reader):
    result = {}

    for line, row in enumerate(csv_reader):
        line += 1

        try:
            class_name, class_id = row
        except ValueError:
            raise(ValueError('line {}: format should be \'class_name,class_id\''.format(line)))
        class_id = int(class_id)

        if class_name in result:
            raise ValueError('line {}: duplicate class name: \'{}\''.format(line, class_name))
        result[class_name] = class_id
    return result


# Draws a caption above the box in an image
def draw_caption(image, box, caption):
    b = np.array(box).astype(int)
    cv2.putText(image, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
    cv2.putText(image, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)


def detect_image(image, model_path, class_list):

    with open(class_list, 'r') as f:
        classes = load_classes(csv.reader(f, delimiter=','))

    labels = {}
    for key, value in classes.items():
        labels[value] = key

    model = torch.load(model_path)

    if torch.cuda.is_available():
        model = model.cuda()

    model.training = False
    model.eval()


    #image = cv2.imread(image_path)
    # if image is None:
    #     continue
    image_orig = image.copy()

    rows, cols, cns = image.shape

    smallest_side = min(rows, cols)

    # rescale the image so the smallest side is min_side
    min_side = 608
    max_side = 1024
    scale = min_side / smallest_side

    # check if the largest side is now greater than max_side, which can happen
    # when images have a large aspect ratio
    largest_side = max(rows, cols)

    if largest_side * scale > max_side:
        scale = max_side / largest_side

    # resize the image with the computed scale
    image = cv2.resize(image, (int(round(cols * scale)), int(round((rows * scale)))))
    rows, cols, cns = image.shape

    pad_w = 32 - rows % 32
    pad_h = 32 - cols % 32

    new_image = np.zeros((rows + pad_w, cols + pad_h, cns)).astype(np.float32)
    new_image[:rows, :cols, :] = image.astype(np.float32)
    image = new_image.astype(np.float32)
    image /= 255
    image -= [0.485, 0.456, 0.406]
    image /= [0.229, 0.224, 0.225]
    image = np.expand_dims(image, 0)
    image = np.transpose(image, (0, 3, 1, 2))

    with torch.no_grad():
        image = torch.from_numpy(image)
        if torch.cuda.is_available():
            image = image.cuda()

        st = time.time()
        print(image.shape, image_orig.shape, scale)
        scores, classification, transformed_anchors = model(image.cuda().float())
        print('Elapsed time: {}'.format(time.time() - st))
        idxs = np.where(scores.cpu() > 0.5)

        for j in range(idxs[0].shape[0]):
            bbox = transformed_anchors[idxs[0][j], :]

            x1 = int(bbox[0] / scale)
            y1 = int(bbox[1] / scale)
            x2 = int(bbox[2] / scale)
            y2 = int(bbox[3] / scale)
            label_name = labels[int(classification[idxs[0][j]])]
            print(bbox, classification.shape)
            score = scores[j]
            caption = '{} {:.3f}'.format(label_name, score)
            # draw_caption(img, (x1, y1, x2, y2), label_name)
            draw_caption(image_orig, (x1, y1, x2, y2), caption)
            cv2.rectangle(image_orig, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)

        cv2.imshow('detections', image_orig)
        cv2.waitKey(0)

def video_loop(video_file, model_path, class_list, store=False):
    
    with open(class_list, 'r') as f:
        classes = load_classes(csv.reader(f, delimiter=','))

    labels = {}
    for key, value in classes.items():
        labels[value] = key

    model = torch.load(model_path)

    if torch.cuda.is_available():
        model = model.cuda()

    model.training = False
    model.eval()


    frame_number = 0
    vid = cv2.VideoCapture(video_file)
    ok, frame = vid.read()

    while ok:
        visuals = frame.copy()
        h = frame.shape[0]
        w = frame.shape[1]
        image = frame[...,::-1]
        
        rows, cols, cns = image.shape

        smallest_side = min(rows, cols)

        # rescale the image so the smallest side is min_side
        min_side = 608
        max_side = 1024
        scale = min_side / smallest_side

        # check if the largest side is now greater than max_side, which can happen
        # when images have a large aspect ratio
        largest_side = max(rows, cols)

        if largest_side * scale > max_side:
            scale = max_side / largest_side

        # resize the image with the computed scale
        image = cv2.resize(image, (int(round(cols * scale)), int(round((rows * scale)))))
        rows, cols, cns = image.shape

        pad_w = 32 - rows % 32
        pad_h = 32 - cols % 32

        new_image = np.zeros((rows + pad_w, cols + pad_h, cns)).astype(np.float32)
        new_image[:rows, :cols, :] = image.astype(np.float32)
        image = new_image.astype(np.float32)
        image /= 255
        image -= [0.485, 0.456, 0.406]
        image /= [0.229, 0.224, 0.225]
        image = np.expand_dims(image, 0)
        image = np.transpose(image, (0, 3, 1, 2))

        with torch.no_grad():
            # image_np = np.expand_dims(image_np, 0)
            image = torch.from_numpy(image)
            if torch.cuda.is_available():
                image = image.cuda()

            st = time.time()
            print(image.shape, visuals.shape)
            scores, classification, transformed_anchors = model(image.cuda().float())
            print('Elapsed time: {}'.format(time.time() - st))
            idxs = np.where(scores.cpu() > 0.5)

            for j in range(idxs[0].shape[0]):
                bbox = transformed_anchors[idxs[0][j], :]

                x1 = int(bbox[0] / scale)
                y1 = int(bbox[1] / scale)
                x2 = int(bbox[2] / scale)
                y2 = int(bbox[3] / scale)
                label_name = labels[int(classification[idxs[0][j]])]
                print(bbox, classification.shape)
                score = scores[j]
                caption = '{} {:.3f}'.format(label_name, score)
                # draw_caption(img, (x1, y1, x2, y2), label_name)
                draw_caption(visuals, (x1, y1, x2, y2), caption)
                cv2.rectangle(visuals, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)

            cv2.imshow('detections', visuals)
            k = cv2.waitKey(10)

            if k == 27:
                if store:
                    writer.release()
                break
            
            if k == 32:

                # if video is still left continue creating images
                name = 'images/frame_' + str(frame_number) + '.jpg'
                print('Creating...' + name)

                # writing the extracted images
                cv2.imwrite(name, frame)

            frame_number += 1

            ok, frame = vid.read()



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Simple script for visualizing result of training.')

    parser.add_argument('--video_file', help='Path to video file')
    parser.add_argument('--model_path', help='Path to model', default='model_final.pt')
    parser.add_argument('--class_list', help='Path to CSV file listing class names (see README)', default = 'classes.txt')

    parser = parser.parse_args()

    video_loop(parser.video_file, parser.model_path, parser.class_list, store = False)
