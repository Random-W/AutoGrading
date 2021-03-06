import cv2
import numpy as np 
def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
 
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
 
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
 
	# return the ordered coordinates
	return rect
def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
 
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
 
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
 
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
 
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
 
	# return the warped image
	return warped

def check_include(centre_list,x_centre,y_centre):
	for point in centre_list:
		x_difference = point[0] - x_centre
		y_difference = point[1] - y_centre
		if abs(x_difference)<10 and abs(y_difference)<10:
			return False
	return True

def find_centre(cnts):
	# x_axis is a list, store all the x_axis data of one contour
	# y_axis is a list, store all the y_axis data of same contour
	# cnts[0] is a list of point, which is one rectangle
	centre_list=[]
	for cnt in cnts:
		x_axis =[]
		y_axis =[]
		for point in cnt:
			x_axis.append(point[0][0])
			y_axis.append(point[0][1])
			# print cnts[0][0][0][0]

		x_axis = sorted(x_axis)
		y_axis = sorted(y_axis)
		x_centre = int((x_axis[0]+x_axis[-1])/2)
		y_centre = int((y_axis[0]+y_axis[-1])/2)
		# print "The smallest x coordinate is",x_axis[0]
		# print "The smallest y coordinate is",y_axis[0]
		# print "The biggest x coordinate is",x_axis[-1]
		# print "The biggest y coordinate is",y_axis[-1]
		# print "The centre of this rectangle is (%d,%d)" %(x_centre, y_centre)
		if(check_include(centre_list,x_centre,y_centre)):
			centre_list.append((x_centre,y_centre))
			# print "The centre of this rectangle is (%d,%d)" %(x_centre, y_centre)
	return centre_list

def process_centre_list(centre_list):
	# this function loop want to put same rows of answer area into same list.
	# And use a list to hold all of rows. So it is a 2D list. 
	# the centre_list is in the order of y-axis from small to large. 
	# In this particular case, every row has three question and each question has 4 rectangles.
	# In each line, the y-axis is almost same, so we can calculate the difference between different
	# y-axis to determine whether the two rectangle is in same line.

	# current_total_delta is total difference of y-axis in one row.
	# current_total_delta_copy tries to store the old data in for loop.
	# current_average_number is number of rectangles we calculate
	current_total_delta = 0
	current_total_delta_copy = 0
	current_average_number = 1
	# current_average_delta = current_total_delta/current_average_number
	# current_average_delta_copy tries to store the old data.
	current_average_delta = 0
	current_average_delta_copy = 0

	# row_list is a list of column_list
	# column_list is a list of point of every line of answer area
	row_list = []
	column_list = []

	for i in range(len(centre_list)-1):
		delta_y1 = (centre_list[i+1][1]-centre_list[i][1]) 
		# print delta_y1

		current_total_delta_copy = current_total_delta
		current_total_delta += delta_y1

		current_average_delta = 1.0*current_total_delta / current_average_number
		current_average_number+=1

		if current_average_delta > current_average_delta_copy*3  and current_average_delta_copy != 0:
			# print "this is average number ",current_average_number
			# print "This is current_average_delta " , current_average_delta
			# print "This is current_average_delta_copy  " , current_average_delta_copy

			current_total_delta = current_total_delta_copy   # restore total delta from copy
			column_list.append(centre_list[i])
			row_list.append(column_list)
			
			column_list = []
			current_total_delta = 0
			current_total_delta_copy = 0
			current_average_number = 1
			continue
		column_list.append(centre_list[i])
		current_average_delta_copy = current_average_delta

	return row_list

# This function want to find the answer student choose. 
# centre_list: list. Hold all the coordinate of centre of rectangle.
# thresh1: image object. The image after threshold.
def find_answer(centre_list,thresh1):
	# the point is the centre of rectangle.
	# We choose a 80*80 square, to detect whether there is black pixel in this square.
	for point in centre_list:
		px = 0
		x_start,x_end = point[0]-40, point[0]+40
		y_start,y_end = point[1]-40, point[1]+40
		for x in range(x_start,x_end):
			for y in range(y_start,y_end):
				px += thresh1[y,x]
		# print "this is pixel " , px

		# 1532000 is a threshold. The value under the 1532000 means student has handwriting 
		# in this region.
		if px < 1532000:
			cv2.circle(thresh1,(x-40,y-40),40,(0,0,0))


if __name__ == '__main__':
	
	image = cv2.imread("image/IB_answer_sheet6.png")

	# ratio = 1000.0 / image.shape[1]
	# # new dimension for image
	# dim = (1000, int(image.shape[0] * ratio))
	# # perform the actual resizing of the image and show it
	# # interpolation = cv2.INTER_AREA this is the algorithm we used. Do worry now
	# image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

	ratio = image.shape[0] / 500.0
	orig = image.copy()
	# convert image to grayscale
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# blur the image slightly to remove noise.
	gray = cv2.bilateralFilter(gray, 11, 17, 17) 
	#gray = cv2.GaussianBlur(gray, (5, 5), 0) is an alternative way to blur the image
	# canny edge detection
	edged = cv2.Canny(gray, 30, 200)
	# two threshold method. 
	# The first one is normal threshold method
	# The second one is use Gaussian method which has better effect.
	# ret,thresh1 = cv2.threshold(gray,150,150,cv2.THRESH_BINARY)
	thresh1= cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
	
	# cv2.imshow("gray image", thresh1)
	# cv2.imwrite('thresh1.png',thresh1)
	# cv2.waitKey(15000)

	# find contours in the edged image, keep only the largest ones, and initialize 
	# our screen contour
	# findContours takes three parameter:
	# First parameter: the image we want to find counter. Need to copy since this method will
	# destroy the image.
	# Second parameter: cv2.RETR_TREE tells OpenCV to compute the hierarchy (relationship) 
	# between contours
	# Third parameter: compress the contours to save space using cv2.CV_CHAIN_APPROX_SIMPLE
	try:
		(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	except:
		(_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	#(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	#the number of returned parameter is different depending on the version of openCV
	#for 2.x it is (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	#for 3.x it is (_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	# sort the counter. The reference is the countourArea. And we only get largest 10 
	# countour.
	cnts = sorted(cnts, key = cv2.contourArea,reverse=True)[:1000]
	# cnts = sorted(cnts, key = cv2.contourArea,reverse=True)[:500]

	# a new list to store all the rectangle counter
	cnts_rect = []
	# initialize the screenCnt.
	screenCnt = None

	# loop over our contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		#This function gives the number of vertices of the figure
		#For example, approx returns 4 if the shape is rectangle and 5 if the shape is pentagon
		# k is constant, it can be changing from 0.005 to 0.1
		# k = 0.005
		k = 0.1
		approx = cv2.approxPolyDP(c, k * peri, True)
		# if our approximated contour has four points, then
		# we can assume that we have found our screen
		if len(approx) == 4 and cv2.contourArea(c)>15000:
			screenCnt = approx
			cnts_rect.append(approx)
			# print "this is coutour area ", cv2.contourArea(c)

	# the print is for test		
	# print screenCnt[0][0]

	# to draw the contours in the original image.
	# print len(cnts_rect)
	cv2.drawContours(image, cnts_rect, -1, (0, 255, 0), 3)

	# x_axis is a list, store all the x_axis data of one contour
	# y_axis is a list, store all the y_axis data of same contour
	# cnts[0] is a list of point, which is one rectangle

	centre_list = find_centre(cnts_rect)
	# print len(centre_list)

	centre_list = sorted(centre_list,key= lambda point: point[0])
	# print "The number of centre point " , len(centre_list)

	# # for test.
	i = 0
	print len(centre_list)
	for i in range(138):
		print centre_list[i]
		# cv2.circle(image,centre_list[i],20,(0,0,0))

	row_list = process_centre_list(centre_list)
	find_answer(centre_list,thresh1)

	# cv2.imshow("Game Boy Screen", image)
	# cv2.imshow("gray image", thresh1)

	# cv2.imwrite('messigray.png',image)
	# cv2.imwrite('thresh1.png',thresh1)
	# cv2.waitKey(15000)

	# apply the four point transform to obtain a top-down
	# view of the original image

	# warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
	# warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
	# warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
	# ret,thresh1 = cv2.threshold(warped,80,85,cv2.THRESH_BINARY)
	# cv2.imshow("Binary",thresh1 )
	# warped = warped.astype("uint8") * 255
	# cv2.waitKey(10000)

	# cv2.imwrite('messigray.png',image)























