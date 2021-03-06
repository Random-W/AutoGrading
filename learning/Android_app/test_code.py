#This is a program that handles the actual image processing and 
#answer detection. We are going to build mobile apps based on this
#program and hopefully we will be able to add more functionality to it.
import cv2
from android import Android
droid = Android()
import numpy as np
def rectify(h):
    h = h.reshape((4,2))
    hnew = np.zeros((4,2),dtype = np.float32)
    add = h.sum(1)
    hnew[0] = h[np.argmin(add)]
    hnew[2] = h[np.argmax(add)]

    diff = np.diff(h,axis = 1)
    hnew[1] = h[np.argmin(diff)]
    hnew[3] = h[np.argmax(diff)]

    return hnew
def check_include(centre_list, x_centre, y_centre):
    for point in centre_list:
        x_difference = point[0] - x_centre
        y_difference = point[1] - y_centre
        if abs(x_difference) < 10 and abs(y_difference) < 10:
            return False
    return True


def find_centre(cnts):
    # x_axis is a list, store all the x_axis data of one contour
    # y_axis is a list, store all the y_axis data of same contour
    # cnts[0] is a list of point, which is one rectangle
    centre_list = []
    for cnt in cnts:
        x_axis = []
        y_axis = []
        for point in cnt:
            x_axis.append(point[0][0])
            y_axis.append(point[0][1])
        # print cnts[0][0][0][0]

        x_axis = sorted(x_axis)
        y_axis = sorted(y_axis)
        x_centre = int((x_axis[0] + x_axis[-1]) / 2)
        y_centre = int((y_axis[0] + y_axis[-1]) / 2)
        # print "The smallest x coordinate is",x_axis[0]
        # print "The smallest y coordinate is",y_axis[0]
        # print "The biggest x coordinate is",x_axis[-1]
        # print "The biggest y coordinate is",y_axis[-1]
        # print "The centre of this rectangle is (%d,%d)" %(x_centre, y_centre)
        if (check_include(centre_list, x_centre, y_centre)):
            centre_list.append((x_centre, y_centre))
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

    for i in range(len(centre_list) - 1):
        delta_y1 = (centre_list[i + 1][1] - centre_list[i][1])
        # print delta_y1

        current_total_delta_copy = current_total_delta
        current_total_delta += delta_y1

        current_average_delta = 1.0 * current_total_delta / current_average_number
        current_average_number += 1

        if current_average_delta > current_average_delta_copy * 3 and current_average_delta_copy != 0:
            # print "this is average number ",current_average_number
            # print "This is current_average_delta " , current_average_delta
            # print "This is current_average_delta_copy  " , current_average_delta_copy

            current_total_delta = current_total_delta_copy  # restore total delta from copy
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
def find_answer(centre_list, thresh1):
    # the point is the centre of rectangle.
    # We choose a 80*80 square, to detect whether there is black pixel in this square.
    for point in centre_list:
        px = 0
        x_start, x_end = point[0] - 40, point[0] + 40
        y_start, y_end = point[1] - 40, point[1] + 40
        for x in range(x_start, x_end):
            for y in range(y_start, y_end):
                px += thresh1[y, x]
        # print "this is pixel " , px

        # 1532000 is a threshold. The value under the 1532000 means student has handwriting
        # in this region.
        if px < 1532000:
            cv2.circle(thresh1, (x - 40, y - 40), 40, (0, 0, 0))


# this function want to find the answer rectangle which are not found by findContours
# function
def find_missing_rectangle(centre_list, centre_list_col, x_uncertainty, y_uncertainty):
    row_list = []
    total_list = []
    # print centre_list_col

    base = centre_list_col[0][1]  # use column point as the base
    y_max = base + y_uncertainty  # add base and y_uncertainty
    for i in range(len(centre_list_col)):
        if centre_list_col[i][1] < y_max:
            row_list.append(centre_list_col[i])
        else:
            # in this case, we end up one line, and change to another line
            # so I set a new base.
            y_max = centre_list_col[i][1] + y_uncertainty
            total_list.append(row_list)
            row_list = []  # renew the row_list
            # add the first element of next line into new row_list
            row_list.append(centre_list_col[i])
    # add final row list into total list.
    total_list.append(row_list)

    # ============================================================
    # for test
    # ============================================================
    # sum = 0
    # for i in range(len(total_list)):
    #   # pass
    #   print sorted(total_list[i])
    #   print "length is ", len(total_list[i])
    #   sum += len(total_list[i])
    #   print("\n")
    #   # print "\n"
    # # print(total_list)
    # print sum
    # ============================================================
    # end test
    # ============================================================

    # to get the max_length of a row of question.
    # and then get a base_list of row_list
    max_length = len(total_list[0])
    base_list = []
    for row_list in total_list:
        if len(row_list) > max_length:
            max_length = len(row_list)
            base_list = row_list

    # print "length of half rectangle is ", x_uncertainty
    total_list_copy = []
    # sort base list
    base_list = sorted(base_list)
    for row_list in total_list:
        # print "this is row_list" , row_list
        # print '\n'
        row_list = sorted(row_list)
        if len(row_list) == max_length:
            total_list_copy.append(row_list)
            continue

        for i in range(max_length):
            try:
                base = base_list[i][0] - x_uncertainty
                if row_list[i][0] > base:
                    x_axis = base_list[i][0]
                    y_axis = row_list[0][1]
                    row_list.insert(i, (x_axis, y_axis))
                    centre_list.append((x_axis, y_axis))
                    print "length of row list is ", len(row_list)
                    if len(row_list) == max_length:
                        total_list_copy.append(row_list)
                        break
            except:
                x_axis = base_list[i][0]
                y_axis = row_list[0][1]
                row_list.insert(i, (x_axis, y_axis))
                centre_list.append((x_axis, y_axis))
                if len(row_list) == max_length:
                    total_list_copy.append(row_list)
                    break
    return total_list_copy

# answer_list is a list. It contains x elements, x is rows of the answer sheet. It is also list
# every row_list contains also list which are centre points of rectangle.
def find_answer2(answer_list,number_of_choice,thresh1,pixel=40, number_of_question=40):
    column = len(answer_list[0])/number_of_choice
    assert(column == 3)
    answer = ""

    number_of_question = 0
    for i in range(column):
        for j in range(len(answer_list)):
            boundary = 1532000
            number_of_answer = 0
            while(True):
                # print boundary
                # print number_of_answer
                # print "i j k" , i ,j
                for k in range(i*4,i*4+number_of_choice):
                    point = answer_list[j][k]
                    px = 0
                    x_start, x_end = point[0] - pixel, point[0] + pixel
                    y_start, y_end = point[1] - pixel, point[1] + pixel
                    for x in range(x_start, x_end):
                        for y in range(y_start, y_end):
                            px += thresh1[y, x]
                    # print "this is pixel " , px

                    # 1532000 is a threshold. The value under the 1532000 means student has handwriting
                    # in this region.
                    # print px
                    if px < boundary:
                        cv2.circle(thresh1, (x - pixel, y - pixel), 40, (0, 0, 0))
                        number_of_answer += 1 
                        choice = str(k)
                if number_of_answer == 1:
                    number_of_question += 1
                    answer += choice
                    break
                if number_of_question==40:
                    break
                if number_of_answer == 0:
                    boundary = boundary * (1.01)
                    number_of_answer = 0
                else: 
                    boundary = boundary / 1.01
                    number_of_answer = 0

        if number_of_question==40:
            break

    return answer 
                





if __name__ == '__main__':
    image = cv2.imread("sheet.jpg")

    # ratio = 1000.0 / image.shape[1]
    # # new dimension for image
    # dim = (1000, int(image.shape[0] * ratio))
    # # perform the actual resizing of the image and show it
    # # interpolation = cv2.INTER_AREA this is the algorithm we used. Do worry now
    # image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

    ratio = image.shape[0] / 500.0
    #orig = image.copy()
    res = cv2.resize(image,None,fx=0.4, fy=0.4, interpolation = cv2.INTER_LANCZOS4)
    # res = cv2.resize(image, dst, interpolation=CV_INTER_LINEAR)
    # convert image to grayscale
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    # blur the image slightly to remove noise.
    #gray = cv2.bilateralFilter(gray, 11, 17, 17)
    gray = cv2.GaussianBlur(gray, (5, 5), 0) #is an alternative way to blur the image
    # canny edge detection
    edged = cv2.Canny(gray, 30, 200)
    # two threshold method. 
    # The first one is normal threshold method
    # The second one is use Gaussian method which has better effect.
    # ret,thresh1 = cv2.threshold(gray,150,150,cv2.THRESH_BINARY)
    # thresh1= cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    cv2.imshow("Outline", res)
    (_, cnts, _) =cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    #Now we're only trying to get the largest contour so we only keep the first 10 elements
    cnts = sorted(cnts, key = cv2.contourArea,reverse=True)[:10]
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.005* peri, True)
        #break when we find the first rectangle
        if len(approx) == 4:
            screenCnt = approx
            break
    #draw out the contour
    cv2.drawContours(res, [screenCnt], -1, (0, 255, 0), 2)
    cv2.imshow("Contours",res)
    #warped = four_point_transform(res, screenCnt.reshape(4, 2) * ratio)
    lel = rectify(screenCnt)
    pts2 = np.float32([[0,0],[840,0],[840,1164],[0,1164]])
    M = cv2.getPerspectiveTransform(lel,pts2)
    dst = cv2.warpPerspective(res,M,(840,1164))
    crop_img = dst[440:945,130:700]
    #dst = cv2.resize(dst, (1050, 1455)) 
    cv2.imshow("Warped",dst)
    #print len(screenCnt)
    # convert the warped image to grayscale, then threshold it
    # to give it that 'black and white' paper effect
    gray2=cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Answer area",gray2)
    cv2.imshow("Answer area",crop_img)
    #reset the image to the answer area and redo the whole contour detecting process
    image = crop_img
    orig = image.copy()
    # convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # blur the image slightly to remove noise.
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    # gray = cv2.GaussianBlur(gray, (5, 5), 0) is an alternative way to blur the image
    # canny edge detection
    edged = cv2.Canny(gray, 30, 200)
    # two threshold method.
    # The first one is normal threshold method
    # The second one is use Gaussian method which has better effect.
    # ret,thresh1 = cv2.threshold(gray,150,150,cv2.THRESH_BINARY)
    thresh1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
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

    # (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # the number of returned parameter is different depending on the version of openCV
    # for 2.x it is (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # for 3.x it is (_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # sort the counter. The reference is the countourArea. Since we are trying to get all the boxes in
    #the answer area we keep 1000 elements in the list so we don't miss any possible boxes.
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:1000]

    # a new list to store all the rectangle counter
    cnts_rect = []
    # initialize the screenCnt.
    screenCnt = None

    # loop over our contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        # This function gives the number of vertices of the figure
        # For example, approx returns 4 if the shape is rectangle and 5 if the shape is pentagon
        # k is constant, it can be changing from 0.005 to 0.1
        # k = 0.005
        k = 0.005
        approx = cv2.approxPolyDP(c, k * peri, True)
        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        if len(approx) == 4 and cv2.contourArea(c) > 15000:
            screenCnt = approx
            cnts_rect.append(approx)
        # print "this is coutour area ", cv2.contourArea(c)

    # the print is for test
    # print screenCnt[0][0]

    # to draw the contours in the original image.
    # print len(cnts_rect)
    cv2.drawContours(image, cnts_rect, -1, (0, 255, 0), 3)

    # to find height and length of the rectangle
    height = cnts_rect[0][2][0][1] - cnts_rect[0][0][0][1]
    length = cnts_rect[0][2][0][0] - cnts_rect[0][0][0][0]

    # x_axis is a list, store all the x_axis data of one contour
    # y_axis is a list, store all the y_axis data of same contour
    # cnts[0] is a list of point, which is one rectangle

    centre_list = find_centre(cnts_rect)
    # print len(centre_list)

    # print "this length of centre_list is ", len(centre_list)

    centre_list_col = sorted(centre_list, key=lambda point: point[1])
    # answer_list is a list. It contains x elements, x is rows of the answer sheet. It is also list
    # every row_list contains also list which are centre points of rectangle.
    answer_list = find_missing_rectangle(centre_list, centre_list_col, length // 2, height // 2)

    # ============================================================
    # for test print point in centre list
    # ============================================================
    # print len(answer_list)
    # for list1 in answer_list:
    #     print("the length of list1 is ", len(list1))
    #     for element in list1:
    #         print element

    # print len(answer_list)
    # ============================================================
    # end test
    # ============================================================

    number_of_choice = 4
    answer = find_answer2(answer_list,number_of_choice,thresh1,pixel=40,number_of_question=40)

    print answer

   
    # i = 0
    # print len(centre_list_col)
    # for i in range(150):
    #     print centre_list_col[i]

    centre_list = sorted(centre_list, key=lambda point: point[0])
    # print "The number of centre point " , len(centre_list)

    # # for test.
    # i = 0
    # print len(centre_list)
    # for i in range(138):
    #   print centre_list[i]
    # cv2.circle(image,centre_list[i],20,(0,0,0))

    # row_list = process_centre_list(centre_list)
    # find_answer(centre_list, thresh1)

    # cv2.imshow("Game Boy Screen", image)
    # cv2.imshow("gray image", thresh1)

    cv2.imwrite('contours.png', image)
    cv2.imwrite('thresh1.png',thresh1)
    # cv2.waitKey(15000)

    # apply the four point transform to obtain a top-down
    # view of the original image

    warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
    warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(warped, 80, 85, cv2.THRESH_BINARY)
    # cv2.imshow("Binary",thresh1 )
    warped = warped.astype("uint8") * 255
    cv2.waitKey(10000)

    cv2.imwrite('messigray.png', image)
