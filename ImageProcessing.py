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
	image_gray = cv2.cvtColor(grid ,cv2.COLOR_BGR2GRAY)
	thresh = cv2.adaptiveThreshold(image_gray,255,1,1,11,15)

	#Find countors
	tempimg, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	
	#draw all countours
	count = 0
	for each in enumerate(contours):
		#Code to identify each cell
		M = cv2.moments(contours[count])
		row = int(M['m10']/M['m00'])
		column = int(M['m01']/M['m00'])


		#output image
		#print count, ": ", row, column
		cv2.putText(grid, "0", (row, column), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
		cv2.drawContours(grid, contours, count, (255,255,255), 1)
		count += 1
	cv2.imshow("test", grid)
	cv2.waitKey(0)
	return contours

def create_matrix(c,image):
	#if color red (from colorlist) if in between c's x,y coordinates
		#put 0 in matrix
	#else
		#put 1 in matrix
	return


#This function takes an image and a list of colors, it then individually segments out
#the specified colors meaning two colors specified will create two different output images.
#Currently only the last color specified has its iamge returned
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
#create_matrix(c, image)





