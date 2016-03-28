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
	#([0,0,100], [100,100,255]),

	#blue
	#([115,0,0], [255,100,100]),

	#green
	#([0,115,0], [100,255,100])

]

# loop over the boundaries
for (lower, upper) in boundaries:
	# create NumPy arrays from the boundaries
	lower = np.array(lower, dtype = "uint8")
	upper = np.array(upper, dtype = "uint8")

	#Create adjacency matrix
	#34 W 42 H
	col_counter = 0
	row_counter = 0

	#Source to use: http://www.shogun-toolbox.org/static/notebook/current/Sudoku_recognizer.html

	'''for row in xrange(110, 435, 34):
		for column in xrange(110, 520, 42):
			col_counter += 1
			cv2.putText(image, "0", (row, column), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
		row_counter += 1'''
 
	# find the colors within the specified boundaries and apply
	# the mask
	mask = cv2.inRange(image, lower, upper)
	output = cv2.bitwise_and(image, image, mask = mask)

	cv2.imshow("images", np.hstack([image, output]))
	cv2.waitKey(0)



