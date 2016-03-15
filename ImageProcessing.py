#Source: http://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/
import numpy as np
import cv2

#import the image
image = cv2.imread("PaintMaze.png")

#code the colors to recognize [B, G. R]
boundaries = [
	#white
	([215, 215, 215], [255, 255, 255]),

	#red
	([0,0,100], [100,100,255]),

	#blue
	([115,0,0], [255,100,100]),

	#green
	([0,115,0], [100,255,100])

]

# loop over the boundaries
for (lower, upper) in boundaries:
	# create NumPy arrays from the boundaries
	lower = np.array(lower, dtype = "uint8")
	upper = np.array(upper, dtype = "uint8")
 
	# find the colors within the specified boundaries and apply
	# the mask
	mask = cv2.inRange(image, lower, upper)
	output = cv2.bitwise_and(image, image, mask = mask)

	cv2.imshow("images", np.hstack([image, output]))
	cv2.waitKey(0)