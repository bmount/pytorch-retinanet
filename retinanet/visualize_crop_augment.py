# coding: utf-8

import torch
from dataloader import CropAugmenter
import numpy as np
import cv2 as cv


def make_sample():
    sample_image = np.zeros((1000, 1000, 3), dtype=np.float)
    cv.circle(sample_image, (500, 500), 40, (255, 255, 0))
    sample_label = np.array([[460, 460, 540, 540]])
    as_anno = dict(img=sample_image, annot=sample_label)
    return as_anno

augmenter = CropAugmenter()

while True:
    augmented = augmenter(make_sample())
    print('anno', augmented['annot'])
    anno = augmented['annot'][0]
    c0 = tuple(list(anno[:2]))
    c1 = tuple(list(anno[2:]))
    cv.rectangle(augmented['img'], c0, c1, (0, 255, 255))
    cv.imshow('out', augmented['img'])
    k = cv.waitKey(0)
    if k == 27:
        break

