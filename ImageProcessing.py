#Source: http://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/
import numpy as np
import cv2


def extract_cells(grid):
	#convert to gray
	image_gray = cv2.cvtColor(grid ,cv2.COLOR_BGR2GRAY)
	thresh = cv2.adaptiveThreshold(image_gray,255,1,1,11,15)

	#Find countors
	tempimg, contours ,hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	
	#draw all countours
	count = 0
	for each in enumerate(contours):
		#Code to identify each cell
		M = cv2.moments(contours[count])
		row = int(M['m10']/M['m00'])
		column = int(M['m01']/M['m00'])
		cv2.putText(grid, "0", (row, column), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
		cv2.drawContours(grid, contours, count, (255,255,255), 1)
		count += 1
	cv2.imshow("test", grid)
	cv2.waitKey(0)
	return

def identify_colors(image):
	# loop over the boundaries
	for (lower, upper) in boundaries:
		# create NumPy arrays from the boundaries
		lower = np.array(lower, dtype = "uint8")
		upper = np.array(upper, dtype = "uint8")

		'''#Create adjacency matrix
		#34 W 42 H
		col_counter = 0
		row_counter = 0

	#Source to use: http://www.shogun-toolbox.org/static/notebook/current/Sudoku_recognizer.html

	for row in xrange(110, 435, 34):
		for column in xrange(110, 520, 42):
			col_counter += 1
			cv2.putText(image, "0", (row, column), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
		row_counter += 1'''
 
	# find the colors within the specified boundaries and apply
	# the mask
	mask = cv2.inRange(image, lower, upper)
	output = cv2.bitwise_and(image, image, mask = mask)

	#cv2.imshow("images", np.hstack([image, output]))
	#cv2.imshow("test", image)
	#cv2.waitKey(0)
	return output






#import the image
image = cv2.imread("PaintMaze.png")

#code the colors to recognize [B, G. R]
boundaries = [
	#white
	([215, 215, 215], [255, 255, 255]),

	#red
	#([0,0,100], [100,100,255]),

	#blue
	([115,0,0], [255,100,100]),

	#green
	#([0,115,0], [100,255,100])

]

grid = identify_colors(image)
extract_cells(grid)





