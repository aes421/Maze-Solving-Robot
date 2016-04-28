#Source: http://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/
import numpy as np
import cv2
from scipy import ndimage
import pandas as pd
import copy
import sys

TOP_LEFT = 0
TOP_RIGHT = 1
BOTTOM_RIGHT = 2
BOTTOM_LEFT = 3


X_POS = 1
Y_POS = 0

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
	new_contours = []
	previous_contour = 0
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
			if (max_size != 0):
				new_contours.append(contours[previous_contour])
			previous_contour = count
			grid_contour_row = row
			grid_contour_column = column
			max_size = size
		else:
			new_contours.append(contours[count])
		count += 1

	#draw white lines showing contours
	cv2.drawContours(grid, new_contours, -1, (255,255,255))


	#approx contains x,y coordinates for the 4 corners of the cella
	approx = []
	for each in range(len(new_contours)):
		approx.append(cv2.approxPolyDP(new_contours[each],0.01*cv2.arcLength(new_contours[each],True),True))

	#cv2.imshow("test", grid)
	cv2.waitKey(0)
	return new_contours, approx


def sort_contours(c):

	sorted_list = copy.deepcopy(c)

	sorted_list.sort(key=lambda x: x[0][0][0])
	sorted_list.sort(key=lambda x: x[0][0][1])

	return sorted_list


def pretty_print(m):
	for i in range(len(m)):
		print m[i]
		print




def create_matrix(approx, colorlist):
	#if color red (from colorlist) is in between c's x,y coordinates
		#put 0 in matrix
	#else
		#put 1 in matrix

	row_list = []
	col_list = []
	for each in range(len(approx)):
		if (approx[each][BOTTOM_RIGHT][0][X_POS] not in row_list):
			row_list.append(approx[each][BOTTOM_RIGHT][0][X_POS])
		if (approx[each][BOTTOM_RIGHT][0][Y_POS] not in col_list):
			col_list.append(approx[each][BOTTOM_RIGHT][0][Y_POS])

	ROWNUM = len(row_list)
	COLNUM = len(col_list)


	
	matrix = []
	matrix_row = [] 
	for each in range(len(approx)):
		#print "contour ", each, ": Top left - ", approx[each][TOP_LEFT][0], "Bottom right - ", approx[each][BOTTOM_RIGHT][0]
		found_red= False
		found_green = False
		#these loop uses contansts to help readability
		#print "Contour ", each, ": y values between: ",approx[each][TOP_LEFT][0][Y_POS], "-", approx[each][BOTTOM_RIGHT][0][Y_POS]
		#print "x values between: ",approx[each][TOP_LEFT][0][X_POS], "-", approx[each][BOTTOM_RIGHT][0][X_POS], "\n"
		
		red_color = create_colorlist("red")
		green_color = create_colorlist("green")
		
		for y in range(approx[each][TOP_LEFT][0][Y_POS], approx[each][BOTTOM_RIGHT][0][Y_POS], 10):
			for x in range(approx[each][TOP_LEFT][0][X_POS], approx[each][BOTTOM_RIGHT][0][X_POS]):
				pixel = image[x,y]
				#if pixel is between the values of lower and upper it is red!
				#if (pixel[0] == 36 and pixel[1] == 28 and pixel[2] == 237):
				if (pixel[0] >= red_color[0][0][0] and pixel[0] <= red_color[0][1][0] and
					pixel[1] >= red_color[0][0][1] and pixel[1] <= red_color[0][1][1] and
					pixel[2] >= red_color[0][0][2] and pixel[02] <= red_color[0][1][2]):
					matrix_row.append(1)
					found_red = True
					break
				#if (pixel[0] == 29 and pixel[1] == 230 and pixel[2] == 181):
				if (pixel[0] >= green_color[0][0][0] and pixel[0] <= green_color[0][1][0] and
					pixel[1] >= green_color[0][0][1] and pixel[1] <= green_color[0][1][1] and
					pixel[2] >= green_color[0][0][2] and pixel[02] <= green_color[0][1][2]):
					matrix_row.append(2)
					found_green = True
					break


			if (y+1 == approx[each][BOTTOM_RIGHT][0][Y_POS] and found_red == False and found_green == False):
				matrix_row.append(0)		
			if (len(matrix_row) >= COLNUM):
				matrix.append(matrix_row)
				matrix_row = []
			if (found_red == True or found_green == True):
				break
			
	return matrix

		

def create_colorlist(colors):
	colorlist = []
	#Add RGB values for each color specified when the function was called
	#to the list colorlist

	if "blue" in colors: #204,72, 63
		colorlist.append(([150,10,10], [255,100,100]))
	if "white" in colors:
		colorlist.append(([215, 215, 215], [255, 255, 255]))
	if "red" in colors:#B = 36 G= 28 R = 237
		colorlist.append(([0,0,180], [90,80,255]))
	if "green" in colors:#B =29 G = 230 R = 181
		colorlist.append(([0,180,130], [80,255,230]))

	return colorlist
#This function takes an image and a list of colors, it then individually segments out
#the specified colors meaning two colors specified will create two different output images.
#Currently only the last color specified has its image returned
def identify_colors(image, color):

	
	colorlist = create_colorlist(color)
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
image_name = sys.argv[1]
image = cv2.imread(image_name)

#print (image[243, 140])
grid, colorlist = identify_colors(image, "blue")
c, approx = extract_cells(grid)
approx = sort_contours(approx)
m = create_matrix(approx, colorlist)
pretty_print(m)





