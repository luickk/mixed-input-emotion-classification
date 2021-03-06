import csv
import os
import numpy as np
import pickle
import cv2
import glob
from imutils import face_utils
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split

def generateDataBatches(files, batch_size, val_training_factor):
    i = 0
    while True:
        for filename in glob.iglob(files):
            i += 1

            data = np.load(filename, allow_pickle=True)
            dataX = np.array(data[0][0])
            dataY = np.array(data[2])

            for cbatch in range(0, dataX.shape[0], batch_size):
                batch_x = dataX[cbatch:(cbatch + batch_size),:,:]
                batch_y = dataY[cbatch:(cbatch + batch_size), :]

                batch_x_training, batch_x_val = np.split(batch_x, [int(val_training_factor * len(batch_x))])
                batch_y_training, batch_y_val = np.split(batch_y, [int(val_training_factor * len(batch_y))])

                yield (batch_x_training, batch_y_training)

def generateValDataBatches(files, batch_size, val_training_factor):
    i = 0
    while True:
        for filename in glob.iglob(files):
            i += 1

            data = np.load(filename, allow_pickle=True)

            dataX = np.array(data[0][0])
            dataY = np.array(data[2])

            for cbatch in range(0, dataX.shape[0], batch_size):
                batch_x = dataX[cbatch:(cbatch + batch_size),:,:]
                batch_y = dataY[cbatch:(cbatch + batch_size), :]

                batch_x_training, batch_x_val = np.split(batch_x, [int(val_training_factor * len(batch_x))])
                batch_y_training, batch_y_val = np.split(batch_y, [int(val_training_factor * len(batch_y))])

                yield (batch_x_val, batch_y_val)


def getDataMetric(files, batch_size, val_training_factor):
    i = 0
    batch_count = 0

    for filename in glob.iglob(files):
        i += 1

        data = np.load(filename, allow_pickle=True)
        dataX = np.array(data[0][0])     

        for cbatch in range(0, dataX.shape[0], batch_size):
            batch_count += 1

    train_batch_count = int(val_training_factor * batch_count)
    val_batch_count = batch_count - train_batch_count

    return train_batch_count, val_batch_count

def generateMixedInputDataBatches(files, batch_size, val_training_factor):
    i = 0
    while True:
        for filename in glob.iglob(files):
            i += 1

            data = np.load(filename, allow_pickle=True)

            dataImageX = np.array(data[0][0])
            dataImageMarkerX = np.array(data[1])
            dataY = np.array(data[2])

            for cbatch in range(0, dataImageX.shape[0], batch_size):
                batchImageX = dataImageX[cbatch:(cbatch + batch_size),:,:]
                batchImageMarkerX = dataImageMarkerX[cbatch:(cbatch + batch_size),:]
                batchY = dataY[cbatch:(cbatch + batch_size), :]

                batchImageXtraining, batchImageXtrainingVal = np.split(batchImageX, [int(val_training_factor * len(batchImageX))])
                batchImageMarkerXtraining, batchImageMarkerXtrainingVal = np.split(batchImageMarkerX, [int(val_training_factor * len(batchImageMarkerX))])
                batchYtraining, batchYtrainingVal = np.split(batchY, [int(val_training_factor * len(batchY))])
                yield [batchImageMarkerXtraining, batchImageXtraining], batchYtraining

def generateMixedInputValDataBatches(files, batch_size, val_training_factor):
    i = 0
    while True:
        for filename in glob.iglob(files):
            i += 1

            data = np.load(filename, allow_pickle=True)

            dataImageX = np.array(data[0][0])
            dataImageMarkerX = np.array(data[1])
            dataY = np.array(data[2])

            for cbatch in range(0, dataImageX.shape[0], batch_size):
                batchImageX = dataImageX[cbatch:(cbatch + batch_size),:,:]
                batchImageMarkerX = dataImageMarkerX[cbatch:(cbatch + batch_size),:]
                batchY = dataY[cbatch:(cbatch + batch_size), :]

                batchImageXtraining, batchImageXtrainingVal = np.split(batchImageX, [int(val_training_factor * len(batchImageX))])
                batchImageMarkerXtraining, batchImageMarkerXtrainingVal = np.split(batchImageMarkerX, [int(val_training_factor * len(batchImageMarkerX))])
                batchYtraining, batchYtrainingVal = np.split(batchY, [int(val_training_factor * len(batchY))])

                yield [batchImageMarkerXtrainingVal, batchImageXtrainingVal], batchYtrainingVal

def getClassesForDataSet(dataSetDir):
    classes = []
    for filename in glob.iglob(dataSetDir, recursive=True):
        if os.path.isfile(filename): # filter dirs
            # in windows split by \\
            # print(filename)
            complete_class = filename.split('/')[3]
            
            # print(complete_class)
            if not complete_class in classes:
                classes.append(complete_class)

    # ! raw dataset labeling ise dependent on that order ! sorting classes by alphabet 
    classes.sort()

    return classes

def getPredictionTestSample(batchSize):
    data = np.load("data/labeled_MPI_selected/4.npy", allow_pickle=True)

    dataImageX = np.array(data[0][0])
    dataImageMarkerX = np.array(data[1])
    dataY = np.array(data[2])
    
    return dataImageX[0:batchSize], dataImageMarkerX[0:batchSize], dataY[0:batchSize]

def label_categorisation(data_x, data_y, classes):
    y_final = []
    x_final = []

    for i in range(len(data_y)):
        for c in range(len(classes)):
            if classes[c] == data_y[i]:
                y_final.append(classes.index(classes[c]))
                x_final.append(data_x[i])

    y_final = to_categorical(y_final, num_classes=len(classes))
    x_final = np.array(x_final)

    return x_final, y_final

def detect_face(img, detector, predictor):
    rects = detector(img, 0)
    roi_color = []
    for (i, rect) in enumerate(rects):
        shape = predictor(img, rect)
        shape = face_utils.shape_to_np(shape)

        (x, y, w, h) = face_utils.rect_to_bb(rect)

        roi_color = img[y:y+h, x:x+w]

    return roi_color
