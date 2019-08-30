import sys


import cv2
from PyQt5 import QtCore

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi
from pyueye import ueye
import numpy as np
from PyQt5.QtCore import Qt




class CamDialog(QDialog):
    #face_cascade=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    #eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    def mousePressEvent(self,e):  # e ; QMouseEvent
        print('BUTTON PRESS')
        print('(%d %d)' % (e.x(), e.y()))
        self.mouseButtonKind(e.buttons())
        self.sx = e.x()
        self.sy = e.y()
    def mouseReleaseEvent(self, e): # e ; QMouseEvent
        print('BUTTON RELEASE')
        print('(%d %d)' % (e.x(), e.y()))
        self.mouseButtonKind(e.buttons())
        self.endx = e.x()
        self.endy = e.y()
    def wheelEvent(self, e): # e ; QWheelEvent
        print('wheel')
        print('(%d %d)' % (e.angleDelta().x(), e.angleDelta().y()))
  #  def mouseMoveEvent(self, e): # e ; QMouseEvent
  #      print('(%d %d)' % (e.x(), e.y()))

    def mouseButtonKind(self, buttons):
        if buttons & Qt.LeftButton: print('LEFT')
        if buttons & Qt.MidButton: print('MIDDLE')
        if buttons & Qt.RightButton: print('RIGHT')

    def __init__(self):
        super(CamDialog, self).__init__()
        loadUi('cam.ui', self)
        self.image=None
        self.roi_color=None
        self.startButton.clicked.connect(self.start_webcam)
        self.stopButton.clicked.connect(self.stop_webcam)
#        self.detectButton.setCheckable(True)
#        self.detectButton.toggled.connect(self.detect_webcam_face)
        self.face_Enabled=False
        self.faceCascade=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        self.hCam = ueye.HIDS(0)  # 0: first available camera;  1-254: The camera with the specified camera ID
        self.sInfo = ueye.SENSORINFO()
        self.cInfo = ueye.CAMINFO()
        self.pcImageMemory = ueye.c_mem_p()
        self.MemID = ueye.int()
        self.rectAOI = ueye.IS_RECT()
        self.pitch = ueye.INT()
        self.nBitsPerPixel = ueye.INT(24)  # 24: bits per pixel for color mode; take 8 bits per pixel for monochrome
        self.channels = 3  # 3: channels for color mode(RGB); take 1 channel for monochrome
        self.m_nColorMode = ueye.INT()  # Y8/RGB16/RGB24/REG32
        self.bytes_per_pixel = int(self.nBitsPerPixel / 8)

        self.nRet = ueye.is_InitCamera(self.hCam, None)
        self.nRet = ueye.is_GetCameraInfo(self.hCam, self.cInfo)
        self.nRet = ueye.is_GetSensorInfo(self.hCam, self.sInfo)
        self.nRet = ueye.is_ResetToDefault(self.hCam)
        self.nRet = ueye.is_SetDisplayMode(self.hCam, ueye.IS_SET_DM_DIB)
        ueye.is_GetColorDepth(self.hCam, self.nBitsPerPixel, self.m_nColorMode)
        self.nRet = ueye.is_AOI(self.hCam, ueye.IS_AOI_IMAGE_GET_AOI, self.rectAOI, ueye.sizeof(self.rectAOI))
        self.width = self.rectAOI.s32Width
        self.height = self.rectAOI.s32Height
        self.nRet = ueye.is_AllocImageMem(self.hCam, self.width, self.height, self.nBitsPerPixel, self.pcImageMemory, self.MemID)
        self.nRet = ueye.is_SetImageMem(self.hCam, self.pcImageMemory, self.MemID)
        self.nRet = ueye.is_SetColorMode(self.hCam, self.m_nColorMode)
        self.nRet = ueye.is_CaptureVideo(self.hCam, ueye.IS_DONT_WAIT)
        self.nRet = ueye.is_InquireImageMem(self.hCam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
        self.xp=[]
        self.yp=[]
        self.lxp=[]
        self.lyp = []
        self.rxp = []
        self.ryp = []
        self.sx = 200
        self.sy = 150
        self.endx = 600
        self.endy = 450

   #     self.avgx = 0
    #    self.avgy = 0
        self.holeflag = 0
        self.lflag = 0
        self.rflag = 0

    def detect_webcam_face(self,status):
        if status:
            self.detectButton.setText('Stop Diagnosis')
            self.face_Enabled=True
        else:
            self.detectButton.setText('Start Diagnosis')
            self.face_Enabled = False


    def start_webcam(self):
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)







    def update_frame(self):
        if (self.nRet == ueye.IS_SUCCESS):

            lowerBound = np.array(150)
            upperBound = np.array(255)

            self.array = ueye.get_data(self.pcImageMemory, 1600, 1200, 32, 6400, copy=False)
            self.frame = np.reshape(self.array, (1200, 1600, 4))
            self.image = cv2.resize(self.frame, (0, 0), fx=0.5, fy=0.5)
           # cv2.imwrite("noname.jpg", self.image)
            self.image = cv2.cvtColor(np.array(self.image), cv2.COLOR_BGR2RGB)
            self.image = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
            self.roi=self.image[self.sy-70:self.endy-70,self.sx-20:self.endx-20]
          #  self.roi[:,int(self.roi.shape[1]/2-20):int(self.roi.shape[1]/2+20)]=0
      #      cv2.imshow('c', self.roi)
            self.grey = cv2.cvtColor(np.array(self.image), cv2.COLOR_BGR2GRAY)
            self.ggg = cv2.cvtColor(np.array(self.roi), cv2.COLOR_BGR2GRAY)

       #     cv2.imshow('c', self.ggg)
            #self.mask = cv2.inRange(self.grey, lowerBound, upperBound)

            ret1, self.mask = cv2.threshold(self.ggg, 220, 255, 0)
            ret1, self.ggg = cv2.threshold(self.ggg, 50, 255, 0)
            self.ggg[:, int(self.ggg.shape[1] / 2 - 20):int(self.ggg.shape[1] / 2 + 20)] = 0
            blur_img = cv2.GaussianBlur(self.ggg, (7, 7), 7)  # Blur 효과335
            edges = cv2.Canny(blur_img, 30, 30, 100)
            #ret1, edges  = cv2.threshold(edges , 100, 255, 0)
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=10)
            edges = cv2.erode(edges, kernel, iterations=12)
            #edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)

         #   cv2.imshow('b', edges)
            #            # self.xxxx.find(255)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 10, 10, 5)
          #  circles=cv2.
            if lines is not None :
                for line in lines:
                    x1,y1,x2,y2=line[0]
                    cv2.line(self.roi, (x1, y1), (x2, y2), (0, 255, 0), 2)


            cv2.rectangle(self.image, (self.sx-20,self.sy-70),
                          (self.endx-20,self.endy-70),
                          (0, 0, 255), 1)
    #            cv2.circle(self.mask,i[0],i[1],i[2],(0,255,0),2)
         #   src_width = self.mask.shape[1]
            roih=self.ggg.shape[0]
            roiw = self.ggg.shape[1]
            for w in range(0,roiw):
                for h in range(0,roih):
                    if self.mask[h,w]==255:
                        self.xp.append(w)
                        self.yp.append(h)
                        self.holeflag=1
            for w in range(0, int(roiw/2)):
                for h in range(0, roih-7):
                    if edges[h, w] == 255 and edges[h, w+1] == 0:
                        self.lxp.append(w)
                        self.lyp.append(h)
                        self.lflag = 1
            for w in range(int(roiw/2), roiw - 7):
                for h in range(0, roih - 7):
                    #    cv2.circle(self.image, (w + self.sx - 20, h + self.sy - 70), 5, (255, 0, 0))
                    if edges[h, w] == 0 and edges[h, w+1] == 255:
                        self.rxp.append(w)
                        self.ryp.append(h)
                        self.rflag =1
                    #    cv2.circle(self.image, (w + self.sx - 20, h + self.sy - 70), 5, (0, 255, 0))

                      #      self.xp.append(w)
                         #   self.yp.append(h)
                         #   self.holeflag = 1
                 #       cv2.circle(self.image, (w+self.sx-20,h+self.sy-70), 20, (0, 255, 0))
                  #      break


            if self.holeflag==1:
                avgx = int(round(np.mean(self.xp)))
                avgy = int(round(np.mean(self.yp)))
                sizeh = abs(max(self.xp) - min(self.xp)) * 0.5 + abs(max(self.yp) - min(self.yp)) * 0.5
                cv2.circle(self.image, (avgx + self.sx - 20, avgy+ self.sy - 70), 20, (0, 255, 0))
                str = "Hole error"
                cv2.putText(self.image, str,(int(avgx) + self.sx - 20, int(avgy) + self.sy - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 255, 255), 1)
                self.xp.clear()
                self.yp.clear()
                self.holeflag =0
            if self.lflag==1:
                avgx = int(round(np.max(self.lxp)))
                avgy = int(round(np.max(self.lyp)))
                self.gapl=avgy
                cv2.circle(self.image, (avgx + self.sx - 20, avgy + self.sy - 70), 5, (0, 0, 255))
                self.lxp.clear()
                self.lyp.clear()
                self.lflag = 0
                print("rpoint %d ,%d"% (avgx,avgy))

            if self.rflag==1:
                avgx = int(round(np.min(self.rxp)))
                avgy = int(round(np.max(self.ryp)))
                self.gapr = avgy
                cv2.circle(self.image, (avgx + self.sx - 20, avgy + self.sy - 70), 5, (255, 0, 0))
                self.rxp.clear()
                self.ryp.clear()
                self.rflag = 0
                print("bpoint %d ,%d" % (avgx, avgy))

            if  abs(self.gapr- self.gapl)>10 :
                str = "Matching error"
                cv2.putText(self.image, str, (self.endx - 20, self.endy - 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 255, 255), 1)



            #contours, _ = cv2.findContours(thr, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)


      #      cv2.imshow('b', edges)




          #  currentMouseX, currentMouseY = self.imglabel.position()
        #    print( currentMouseX, currentMouseY)
         #   position =pos().x(), pos().y()
            self.displayImage(self.image, 1)
        #    self.displayImage(color_mask, 1)
            #self.image = cv2.cvtColor(np.array(self.image), cv2.COLOR_BGR2RGB)
        #    img2=self.image.copy()
            #img = cv2.imread('noname.jpg', 1)
            #greyimg=cv2.cvtColor(np.array(self.image), cv2.COLOR_HSV2GRAY)
            #hsv = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV)
          #  Gmask = cv2.inRange(self.image, lowerBound, upperBound)
         #   ret1, thr = cv2.threshold(Gmask, 127, 255, 0)


           # ret,img_b=cv2.threshold(thr,0,127,0)
       #     contours, hierarchy=cv2.findContours(thr,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
          #  for cnt in contours:
          #      cv2.drawContours(img2,[cnt],0,(255,0,0),3)
         #   cv2.imshow('h', img2)
           # imgray=np.float32(greyimg)
          #  dst=cv2.cornerHarris(imgray,2,3,0.04)
         #   dst=cv2.dilate(dst,None)
          #  img2[dst>0.01*dst.max()]=[255,0,0]
            #cv2.imshow('h',img2)
          #  blur_img = cv2.GaussianBlur(greyimg, (7,7),11)  # Blur 효과


         #   edges=cv2.Canny(blur_img,10,50,10)
          #  lines = cv2.HoughLinesP(edges, 1, np.pi / 180,30, 700, 200)
        #    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, 10, 10)
       #     for line in lines:
        #        x1,y1,x2,y2=line[0]
       #         cv2.line(self.image, (x1, y1), (x2, y2), (0, 255, 0), 2)

         #   for line in lines:
          #      r,theta=line[0]
          #      a=np.cos(theta)
           #     b=np.sin(theta)
           #     x0=a*r
            #    y0=b*r
            #    x1=int(x0+1000*(-b))
           #     y1=int(y0+1000*a)
           #     x2=int(x0-1000*(-b))
          #      y2=int(y0-1000*a)
           #     cv2.line(self.image,(x1,y1),(x2,y2),(0,255,0),1)/#



        #    cv2.imshow('img',edges)
            # Press q if you want to end the loop


       # self.image = cv2.resize(frame, (0, 0), 620, 480)
       #    if(self.face_Enabled):
        #        detect_image=self.detect_face(self.image)
        #        roi_image = self.detect_face_roi(self.image)
           # roi_image = self.detect_face_roi(self.image)
          #      self.displayImage(detect_image, 1)
          #      self.displayImage(roi_image, 2)
         #   else:
        #        self.displayImage(self.image,1)
            #elf.displayImage(self.image, 2)


    def detect_face(self,img):
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        face=self.faceCascade.detectMultiScale(gray,1.3,5, minSize=(90,90))

        for(x,y,w,h) in face:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)


        return img

    def detect_face_roi(self,img):
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        face=self.faceCascade.detectMultiScale(gray,1.3,5, minSize=(90,90))

        for(x,y,w,h) in face:
            img = img[y:y + h, x:x + w]

        img=cv2.resize(img,(320,240))


        return img



    def stop_webcam(self):
        self.timer.stop()


    def displayImage(self,img,window=2):
        qformat=QImage.Format_Indexed8
        if len(img.shape)==3 :
            if img.shape[2]==4 :
                qformat=QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage=QImage(img,img.shape[1],img.shape[0],img.strides[0],qformat)
        outImage=outImage.rgbSwapped()
        if window==1:
            self.imglabel.setPixmap(QPixmap.fromImage(outImage))
            self.imglabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        if window==2:
            self.facelabel.setPixmap(QPixmap.fromImage(outImage))
            self.facelabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)





if __name__=='__main__':
    app = QApplication(sys.argv)
    window = CamDialog()
    window.setWindowTitle('Stress Diagnosis ')
    window.show()
    sys.exit(app.exec_())
