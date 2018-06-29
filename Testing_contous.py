import cv2
import numpy as np
from math import atan,degrees
def min_max(array):	
	xmin=9999
	xmax=-9999
	ymin=9999
	ymax=-9999
	for i in range(0,len(array)):
		xmin=min(xmin,array[i][0][0])
		xmax=max(xmax,array[i][0][0])
		ymin=min(ymin,array[i][0][1])
		ymax=max(ymax,array[i][0][1])
	return xmin-0,xmax+0,ymin-0,ymax+0

def dist(p1,p2):
	return(int(((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**(0.5)))
# def get_borders(image):
# 	im=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
# 	row_m=image.flatten()
# 	col_m=image.flatten('F')
# 	xmin=9999
# 	xmax=-9999
# 	ymin=9999
# 	ymax=-9999
# 	for i in range (len(row_m)):
# 		if(row_m[i]!=0):
# 			xmin=min(xmin,i%im.shape[0])
# 			xmax=max(xmax,i%im.shape[0])
# 	for i in range (len(col_m)):
# 		if(col_m[i]):
# 			ymin=min(ymin,i%im.shape[1])
# 			ymax=max(ymax,i%im.shape[1])

# 	print(xmin,xmax,ymin,ymax)
# 	return xmin,xmax,ymin,ymax


def rotate(image,contour,pos):
	rect=cv2.minAreaRect(contour)
	box=cv2.boxPoints(rect)
	box=np.int0(box)
	p1=[box[0][0]-pos[0],box[0][1]-pos[2]]
	p2=[box[1][0]-pos[0],box[1][1]-pos[2]]
	p3=[box[2][0]-pos[0],box[2][1]-pos[2]]
	# p4=[box[3][0]-pos[0],box[3][1]-pos[2]]
	# print([p1,p2,p3,p4])
	ht = dist(p1,p2)
	w = dist(p2,p3)
	print("ht=",ht,"w=",w)
	M=cv2.moments(contour)
	cx = int(M['m10']/M['m00'])
	cy = int(M['m01']/M['m00'])

	cx = cx-pos[0]+max(ht,w)
	cy = cy-pos[2]+max(ht,w)
	# c1=np.zeros(image.shape)
	# i=cv2.line(c1,(p1[0],p1[1]),(p2[0],p2[1]),(255,0,0),3)
	# i1=cv2.line(i,(p3[0],p3[1]),(p2[0],p2[1]),(255,0,0),3)
	# i2=cv2.line(i1,(p4[0],p4[1]),(p3[0],p3[1]),(255,0,0),3)
	# i3=cv2.line(i2,(p1[0],p1[1]),(p4[0],p4[1]),(255,0,0),3)
	# cv2.imshow("",i3)
	# cv2.waitKey(0)
	shape=(image.shape[0]+2*max(ht,w),image.shape[1]+2*max(ht,w),image.shape[2])
	canvas=np.zeros(shape,np.uint8)
	angle=degrees(atan(float((p1[0]-p2[0])/(p1[1]-p2[1]))))
	print("angle=",angle)
	# cx = canvas.shape[1]//2
	# cy = canvas.shape[0]//2
	rotMat=cv2.getRotationMatrix2D((cx,cy),-angle,1)
	canvas[max(ht,w):image.shape[0]+max(ht,w) , max(ht,w):image.shape[1]+max(ht,w) , :] = image[:,:,:]

	canvas = cv2.warpAffine(canvas,rotMat,(canvas.shape[0],canvas.shape[1]))
	# i=cv2.line(canvas,(cx+w//2,cy),(cx-w//2,cy),(255,0,0),2)
	# i=cv2.line(i,(cx,cy+ht//2),(cx,cy-ht//2),(255,0,0),2)
	#xmin,xmax,ymin,ymax=get_borders(canvas)
	# print(min_max(c))
	return(canvas[cy-ht//2:cy+ht//2,cx-w//2:cx+w//2,:])


def area(img):
	return img[0].shape[0]*img[0].shape[1]

def aspect_ratio(img):
	return float(img[0].shape[1]/img[0].shape[0])

def inside(im1,im2):
	b=im1[1][0]>=im2[1][0] and im1[1][1]<=im2[1][1] and im1[1][2]>=im2[1][2] and im1[1][3]<=im1[1][3]
	return b

def compress(recs):
	recs=sorted(recs,key=area)
	recs=[x for x in recs if area(x)>10000]
	recs=[x for x in recs if aspect_ratio(x)>0.499999999 and aspect_ratio(x)<2]
	imgs=[]	
	pos=[]
	for i in range(0,len(recs)):
		#print(i)
		f=0 	
		for j in range(i+1,len(recs)):
			if inside(recs[i],recs[j]) == True:
				f=1
				break
		if f == 0:
			#print(j)
			imgs.append(rotate(recs[i][0],recs[i][2],recs[i][1]))
			pos.append([recs[i][1][0],recs[i][1][2]])
	return(imgs,pos)

def get_smaller_images(path='Test1.jpg'):
	image=cv2.imread(path)
	#Might wanna resize here
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.bilateralFilter(gray, 11, 17, 17)
	# cv2.imshow("",gray)
	# cv2.waitKey(0)
	edged = cv2.Canny(gray, 30, 200)
	(__,cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	cnts = sorted(cnts,key = cv2.contourArea, reverse = True)
	ret=[]
	#cv2.drawContours(image,cnts,-1,(255,0,0),3)
	for c in cnts:
		xmin,xmax,ymin,ymax=min_max(c)
		# print(min_max(c))
		ret.append((image[ymin:ymax,xmin:xmax,:],[xmin,xmax+xmin,ymin,ymax+ymin],c))

	imgs,pos=compress(ret)
	print(pos)
	return imgs,pos

import matplotlib.pyplot as plt
imgs,_ = get_smaller_images()
for i in range(len(imgs)):
	cv2.imwrite(str(i)+".jpg",imgs[i])


