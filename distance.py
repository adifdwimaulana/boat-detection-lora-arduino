# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from imutils.video import FileVideoStream
import numpy as np
import argparse
import imutils
import time
import cv2
from math import sqrt
# import serial

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# ser = serial.Serial('COM8', 9600, write_timeout=0)

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "boat"]

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
# print("[INFO] starting video stream...")
# vs = VideoStream(src=1).start()
vs = FileVideoStream("test.mp4").start()
# vs = FileVideoStream("56623.t.mp4").start()
time.sleep(2.0)
fps = FPS().start()
counter = 0

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
    frame = vs.read()
	# frame = imutils.resize(frame, width=400)
	# grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
	# pass the blob through the network and obtain the detections and
	# predictions
    net.setInput(blob)
    detections = net.forward()
    botX = int(w/2)
    botY = h
    botCenter = (botX, botY)

    	# loop over the detections
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
		# filter out weak detections by ensuring the `confidence` is
		# greater than the minimum confidence
        if confidence > args["confidence"]:
			# extract the index of the class label from the
			# `detections`, then compute the (x, y)-coordinates of
			# the bounding box for the object
			# print("Detected")
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
			# draw the prediction on the frame
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0,255,0), 2)
            centerX = int((startX+endX)/2)
            centerY = int((startY+endY)/2)
            # print("x: ", centerX)
            # print("y: ", centerY)
            boxCenter = (centerX, centerY)
            # print("Center: ", boxCenter)
            # print("Bottom: ", botCenter)
            distance = 0
            if centerX == botX:
                distance = botY - centerY
            else:
                line = (centerX, botY)
                tinggi = abs(int(botY - centerY) * int(botY - centerY))
                alas = abs(int(botX - centerX) * int(botX - centerX))
                distance = sqrt(alas + tinggi)

            print("Distance: ", distance)
            cv2.line(frame, boxCenter, botCenter, (0,255,0), 2)
            text = "Jarak = " + str(int(distance)) + " pixels"
            cv2.putText(frame, text, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
		
	# show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
	# if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
	# update the FPS counter
    fps.update()

    # stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
