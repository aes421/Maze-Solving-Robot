#Source: http://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/
import numpy as np
import cv2

'''Extreme points 
leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])'''


def extract_cells(grid):

	#convert to gray
	image_gray = cv2.cvtColor(grid, cv2.COLOR_BGR2GRAY)
	#creates a binary image from the gray scale image to use as input for findContours()
	#thresh = cv2.adaptiveThreshold(image_gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,11,15)

	#Find countors
	tempimg, contours, hierarchy = cv2.findContours(image_gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	

	#draw all countours
	count = 0
	max_size = 0
	matrix = [] 
	new_contours = []
	grid_contour = 0
	grid_contour_row = None
	grid_contour_column = None
	for each in enumerate(contours):
		
		#used to find the midpoint of each cell
		M = cv2.moments(contours[count])
		row = int(M['m10']/M['m00'])
		column = int(M['m01']/M['m00'])

		#find biggest box (this is the grid itself, so needs to be removed since it is not a cell)
		size = cv2.contourArea(contours[count])
		if (size > max_size):
			new_contours.append(contours[grid_contour])
			#put a marker in each cell for testing
			if (grid_contour_row != None and grid_contour_column != None):
				cv2.putText(grid, "0", (grid_contour_row, grid_contour_column), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
			grid_contour = count
			grid_contour_row = row
			grid_contour_column = column
		else:
			new_contours.append(contours[count])
			#put a marker in each cell for testing
			cv2.putText(grid, "0", (row, column), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))

		
		
		matrix = create_matrix(matrix,count)
		count += 1

	#draw white lines showing contours
	
	cv2.drawContours(grid, new_contours, -1, (255,255,255))
	print (matrix)


	cv2.imshow("test", grid)
	cv2.waitKey(0)
	return contours

def create_matrix(matrix, count):
	#if color red (from colorlist) if in between c's x,y coordinates
		#put 0 in matrix
	#else
		#put 1 in matrix
	matrix.append(count)
	return matrix


#This function takes an image and a list of colors, it then individually segments out
#the specified colors meaning two colors specified will create two different output images.
#Currently only the last color specified has its image returned
def identify_colors(image, *colors):

	colorlist = []
	#Add RGB values for each color specified when the function was called
	#to the list colorlist

	if "blue" in colors:
		colorlist.append(([115,0,0], [255,100,100]))
	if "white" in colors:
		colorlist.append(([215, 215, 215], [255, 255, 255]))
	if "red" in colors:
		colorlist.append(([0,0,100], [100,100,255]))
	if "green" in colors:
		colorlist.append(([0,115,0], [100,255,100]))

	#loop over the colorlist
	for (lower, upper) in colorlist:
		# create NumPy arrays from the colorlist
		lower = np.array(lower, dtype = "uint8")
		upper = np.array(upper, dtype = "uint8")


	
		#econverts image to b/w with white being anything in the BGR value range
		mask = cv2.inRange(image, lower, upper)
		#converts that specified range back to its orginal color
		output = cv2.bitwise_and(image, image, mask = mask)

		#show the photos side by side
		#cv2.imshow("images", np.hstack([image, output]))
		#cv2.waitKey(0)
		
	return output
	






#import the image
image = cv2.imread("minimaze.png")


grid = identify_colors(image, "blue")
c = extract_cells(grid)






