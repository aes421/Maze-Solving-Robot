#Source: http://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/
import numpy as np
import cv2
from scipy import ndimage
import pandas as pd

ROWNUM = 2
COLNUM = 2

def centroid(contour):
    x,y,w,h = cv2.boundingRect(contour)
    return (y+h/2.0, x+w/2.0)

def contains_red(red_mask, tile):
    tile_area = np.zeros_like(red_mask)
    cv2.drawContours(tile_area, [tile[1]], 0, 255, -1)
    red_tile_area = cv2.bitwise_and(tile_area, red_mask)
    return (cv2.countNonZero(red_tile_area))

def get_transform(grid_size, grid_contour):
    x,y,w,h = cv2.boundingRect(grid_contour)
    tile_w = float(w) / (grid_size[0])
    tile_h = float(h)/ (grid_size[1])
    return ((-y - tile_h/2, -x - tile_w/2), (1/tile_h, 1/tile_w))

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
			grid_contour = count
			grid_contour_row = row
			grid_contour_column = column
		else:
			new_contours.append(contours[count])
			

		
		
		#matrix = create_matrix(matrix,count)
		count += 1

	#draw white lines showing contours
	cv2.drawContours(grid, new_contours, -1, (255,255,255))


	#approx contains x,y coordinates for the 4 corners of the cell
	approx = cv2.approxPolyDP(contours[0],0.01*cv2.arcLength(contours[0],True),True)
	

	#cv2.imshow("test", grid)
	#cv2.waitKey(0)
	return new_contours, approx

def create_matrix(contours, approx):
	#if color red (from colorlist) is in between c's x,y coordinates
		#put 0 in matrix
	#else
		#put 1 in matrix


	red_mask, red = identify_colors(image, "red")
	blue_mask, blue = identify_colors(image, "blue")
	grid_area = np.zeros_like(blue_mask)
	grid_tiles = cv2.bitwise_and(cv2.bitwise_not(blue_mask), grid_area)


	isblue = cv2.inRange(image, np.array(blue[0][0]), np.array(blue[0][1]))
	isred = cv2.inRange(image, np.array(red[0][0]), np.array(red[0][1])) > 0

	# Find scaling parameters
	offset, scale = get_transform((ROWNUM, COLNUM), contours[0])

	tiles = [[centroid(contour), contour, False] for contour in contours]
	for tile in tiles:
    	# Rescale centroid
		tile[0] = (int(round((tile[0][0] + offset[0]) * scale[0])), int(round((tile[0][1] + offset[1]) * scale[1])))
    	tile[2] = contains_red(red_mask, tile)

	# Sort the tiles
	tiles = sorted(tiles, key=lambda x: x[0], reverse=False)

	# Extract the results
	result = np.array([int(t[2]) for t in tiles])

	print result.reshape(ROWNUM,COLNUM)



		#if (count > COLNUM - 1):
		#	matrix.append(templist)
		#	templist = []
		#	count = 0
		#templist.append(0)

	return 0

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

		# Remove outer black area Source: http://stackoverflow.com/questions/36508001/determining-if-a-color-is-within-a-contour-opencv
		flooded = image.copy()
		x = 5
		y = 5
		flooded = output.copy()
		h, w = output.shape[:2]
		mask = np.zeros((h+2, w+2), np.uint8)
		mask[:] = 0
		cv2.floodFill(flooded,mask,(x,y),(255,)*3, (40,)*3, (40,)*3, 4 )

		#show the photos side by side
		#cv2.imshow("images", np.hstack([image, flooded]))
		#cv2.waitKey(0)
		
	return flooded, colorlist
	






#import the image
image = cv2.imread("minimaze.png")

grid, blue = identify_colors(image, "blue")
c, approx = extract_cells(grid)
matrix = create_matrix(c,approx)





