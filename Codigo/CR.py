#https://github.com/gonzalorodriguezrovira/VIA_UMU

import cv2 as cv
import math
from umucv.stream import autoStream
from collections import deque
import numpy as np
from umucv.util import putText


points = deque(maxlen=3)#Variable que contendra mis puntos colocados de manera manual
p2=deque()#Varaible que contendra mis puntos generados nuevos
P=1/4#Constante que se usara para el cross-ratio ya que si sabemos que la distanci entre a=b=c P sera siempre 1/4
P2=1/2#Constante que se usara para el cross-ratio para calcular el punto de fuga ya que si sabemos a la larga si a=b=1 y c=infinto al despejar la formula como limite dara 1/2
puntoFuga=deque()#Variable que contendrá el punto de fuga

def fun(event, x, y, flags, param):#Funcion para marcar los puntos de manera manual
    if event == cv.EVENT_LBUTTONDOWN:
        points.append((x,y))
                       
def puntos(numero):
    
    pts=np.array(points)#Para poder saber la altura estimada de mis puntos dado x trazo una recta entre mis puntos 0 y 2
    m = (pts[2][1] - pts[0][1]) / (pts[2][0] -  pts[0][0])
    b = pts[0][1] - m *  pts[0][0]
    height, width, _ = frame.shape
    x1 = 0
    y1 = int(m * x1 + b)
    x2 = width - 1
    y2 = int(m * x2 + b)
    cv.line(frame, (x1, y1), (x2, y2), (128, 128, 128), 1)#Diubujo la recta
    
    if len(p2)!=numero:#Solo se ejecutará en caso de no tener ya los puntos
        
        for i in range(numero):
        
            if len(p2)==0:
                #Al sabes que p=1/4 y que  p=(a/(a+b))*(c/(c+b)) puedo despejar la formula c = (P * (A+B)/A) * B / (1 - (P * (A+B)/A)) despejando c que seria la distancia desde mi punto c al punto d
                A=points[1][0]-points[0][0]
                B=points[2][0]-points[1][0]
                c = (P * (A+B)/A) * B / (1 - (P * (A+B)/A))
                x=(math.ceil(c)+points[2][0])#Al sumar a mi ultimo punto c obtengo el nuevo punto d
                y=int(m*x + b)#saco la y dado el valor x de mi recta ya que y = m * x + b
                p2.append((x,y))

            else: 
                if len(p2)==1:
                  #Al sabes que p=1/4 y que  p=(a/(a+b))*(c/(c+b)) puedo despejar la formula c = (P * (A+B)/A) * B / (1 - (P * (A+B)/A)) despejando c que seria la distancia desde mi punto c al punto d
                    A=points[2][0]-points[1][0]
                    B=p2[0][0]-points[2][0]
                    c = (P * (A+B)/A) * B / (1 - (P * (A+B)/A))
                    x=(math.ceil(c)+p2[0][0])#Al sumar a mi ultimo punto c obtengo el nuevo punto d
                    y=int(m * (int(c)+p2[0][0]) + b)#saco la y dado el valor x de mi recta ya que y = m * x + b
                    p2.append((x,y))

                else:
                    if len(p2)==2:
                  #Al sabes que p=1/4 y que  p=(a/(a+b))*(c/(c+b)) puedo despejar la formula c = (P * (A+B)/A) * B / (1 - (P * (A+B)/A)) despejando c que seria la distancia desde mi punto c al punto d
                        A=p2[i-2][0]-points[2][0]
                        B=p2[i-1][0]-p2[i-2][0]
                        c = (P * (A+B)/A) * B / (1 - (P * (A+B)/A))
                        x=(math.ceil(c)+p2[i-1][0])#Al sumar a mi ultimo punto c obtengo el nuevo punto d
                        y=int(m * (int(c)+p2[i-1][0]) + b)#saco la y dado el valor x de mi recta ya que y = m * x + b
                        p2.append((x,y))

                    else:
                        if len(p2)>2:
                            A=p2[i-2][0]-p2[i-3][0]
                            B=p2[i-1][0]-p2[i-2][0]
                            c = (P * (A+B)/A) * B / (1 - (P * (A+B)/A))
                            x=(math.ceil(c)+p2[i-1][0])#Al sumar a mi ultimo punto c obtengo el nuevo punto d
                            y=int(m * (int(c)+p2[i-1][0]) + b)#saco la y dado el valor x de mi recta ya que y = m * x + b
                            p2.append((x,y))


def mostrarPuntos(numero):#Funcion para monstrar mis puntos, debe hacerse de manera constante
    
    if numero>0:
        for i in range(numero):
            cv.circle(frame, p2[i],3,(0,0,255),-1)    

def Fuga():
   
    if len(puntoFuga) ==0:
        
        pts=np.array(points)#Saco mi m y b de la recta
        m = (pts[2][1] - pts[0][1]) / (pts[2][0] -  pts[0][0])
        b = pts[0][1] - m *  pts[0][0]
        A=p2[1][0]-p2[0][0]#Obtengo mis ultimos puntos(este caso es para solo 3 artificiales)
        B=p2[2][0]-p2[1][0]
        c = (P2 * (A+B)/A) * B / (1 - (P2 * (A+B)/A))
        x=(int(c)+p2[2][0])#Al sumar a mi ultimo punto c obtengo el nuevo punto d
        y=int(m*x + b)#saco la y dado el valor x de mi recta ya que y = m * x + b
        puntoFuga.append((x,y)) 
        cv.circle(frame, puntoFuga[0],3,(0,0,255),-1)

        
    else:
        
        cv.circle(frame, puntoFuga[0],3,(0,0,255),-1)
    

cv.namedWindow("webcam")
cv.setMouseCallback("webcam", fun)

for key, frame in autoStream(): 
      
    for p in points:#Dibujo mis puntos manuales
        
        cv.circle(frame, p,3,(0,255,0),-1)
        putText(frame,f'{points.index(p)+1}',p)
  
    if len(points) == 3:#En caso de ya tener y tres manuales obtengo y dibujo todo lo demas
        
        cv.line(frame, points[0],points[1],(0,255,0))
        cv.line(frame, points[1],points[2],(0,255,0))
        puntos(3)
        mostrarPuntos(3)
        Fuga()
             
    cv.imshow('webcam',frame)
    
cv.destroyAllWindows()