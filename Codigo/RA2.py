#!/usr/bin/env python

# Detección del marcador ../../images/ref.png

# Puedes probarlo con
#  ./polygon1.py --dev=../../images/rot4.mjpg

# en esta imagen hay figuras parecidas pero que no son el marcador:

#  ./polygon1.py --dev=dir:../../images/polis.png
#https://github.com/gonzalorodriguezrovira/VIA_UMU

import cv2          as cv
import numpy        as np

from umucv.stream   import autoStream
from umucv.htrans   import htrans, Pose
from umucv.util     import cube, showAxes
from umucv.contours import extractContours, redu

def Kfov(sz,hfovd):
    hfov = np.radians(hfovd)
    f = 1/np.tan(hfov/2)
    w,h = sz
    w2 = w / 2
    h2 = h / 2
    return np.array([[f*w2, 0,    w2],
                     [0,    f*w2, h2],
                     [0,    0,    1 ]])

def homog(x):
    ax = np.array(x)
    uc = np.ones(ax.shape[:-1]+(1,))
    return np.append(ax,uc,axis=-1)

def inhomog(x):
    ax = np.array(x)
    return ax[..., :-1] / ax[...,[-1]]

def htrans(h,x):
    return inhomog(homog(x) @ h.T)

def redu(c, eps=0.5):
    red = cv.approxPolyDP(c,eps,True)
    return red.reshape(-1,2)

def polygons(cs,n,prec=2):
    rs = [ redu(c,prec) for c in cs ]
    return [ r for r in rs if len(r) == n ]

destino=()#Variable que contine la posicion a la que debe llegar el cubo 
posicion=()#Variable que contine la posicion en la que se situa el cubo

def cacularVectores(des,posicion):#Funcion para calcular el vector de movimiento y el de rotacion para saber como llegar de un punto a otro
    global vectorM
    global vectorR
    destino=htrans(H,des)
    vectorM=[destino[0]-posicion[0],destino[1]-posicion[1]]
    magnitud = np.linalg.norm(vectorM)
    vectorR = vectorM / magnitud

def fun(event, x, y, flags, param):#Funcion para guardar el destino
    global destino
    if event == cv.EVENT_LBUTTONDOWN:
        destino=(x,y)
        
        
# calculamos la homografía que relaciona un polígono observado con el marcador
# y devolvemos también el error de ajuste
def errorMarker(c):
    H,_ = cv.findHomography(c, marker)
    err = abs(htrans(H,c) - marker).sum()
    return err, H

# genera todas las posibles ordenaciones de puntos
def rots(c):
    return [np.roll(c,k,axis=0) for k in range(len(c))]

# el primer vértice del polígono detectado puede ser cualquiera
# probamos todas las asociaciones y nos quedamos con la que tenga menor error
def bestRot(c):
    return min( [ (errorMarker(r), r) for r in rots(c) ] )

def bestPose(K,view,model):
    poses = [ Pose(K, v.astype(float), model) for v in rots(view) ]
    return sorted(poses,key=lambda p: p.rms)[0]

stream = autoStream()

HEIGHT, WIDTH = next(stream)[1].shape[:2]
size = WIDTH,HEIGHT

K = Kfov( size, 60 )

marker = np.array(
       [[0,   0  ],
        [0,   1  ],
        [0.5, 1  ],
        [0.5, 0.5],
        [1,   0.5],
        [1,   0  ]])

marker2 = np.array(
       [[0,   0,   0],
        [0,   1,   0],
        [0.5, 1,   0],
        [0.5, 0.5, 0],
        [1,   0.5, 0],
        [1,   0,   0]])

cv.namedWindow("source")
cv.setMouseCallback("source", fun)

for n, (key,frame) in enumerate(stream):
   
    g = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    cs = extractContours(g, minarea=5, reduprec=2)
    good = polygons(cs,6,3)
    ok = [ (c,H) for (err, H), c in map(bestRot, good) if err < 0.1 ]
    
    if ok:
        
        c,H = ok[0]
        poses = []

    for g in good:
        
        p = bestPose(K,g,marker2)
        
        if p.rms < 2:
            
            poses += [p.M]
            

    if poses:#Para este ejercicio solo necesito una pose de referencia por lo que al tener una ya podré actuar
        
        M=poses[0]#Me quedo con la primera pose ya que solo necesito actuar sobre una

        x,y = htrans(M, (0.7,0.7,0) ).astype(int)#Capturamos el color de un punto cerca del marcador para borrarlo
        b,g,r = frame[y,x].astype(int)
        cv.drawContours(frame,[htrans(M,marker2).astype(int)], -1, (0,0,0) , 3, cv.LINE_AA)#Dibujando un cuadrado encima

        showAxes(frame, M, scale=0.5)# Mostramos el sistema de referencia inducido por el marcador

        cosa = (cube)* (0.5, 0.5, 0.5)#Creo mi cubo 
        
        posicion=[cosa[0][0], cosa[0][1]]#Obtengo la posicion de mi cubo
                       
        cv.drawContours(frame, [ htrans(M, cosa).astype(int) ], -1, (0,128,0), 3, cv.LINE_AA)#Dibujo el cubo
        
        if len(destino)>0:#En caso de ya tener destino
            
            cacularVectores(destino,posicion)#LLamo a mi funcion para calcular el vector de movimiento y le de rotacion 
                
            if vectorM[0]!=0:#Trato si no se encuentra el cubo en su eje x 

                if(vectorR[0]>0):#En caso de ser mi x menor a la del destino la aumento y creo un nuevo objeto con el cubo

                    cube=cube+(0.05,0,0)

                elif(vectorR[0]<0):#En caso de ser mi x mayor a la del destino la reduzco y creo un nuevo objeto con el cubo

                    cube=cube-(0.05,0,0)
        
            if vectorM[1]!=0:#Trato si no se encuentra el cubo en su eje y

                if(vectorR[1]>0):#En caso de ser mi y menor a la del destino la aumento y creo un nuevo objeto con el cubo

                    cube=cube+(0,0.05,0)


                elif(vectorR[1]<0):#En caso de ser mi y mayor a la del destino la reduzco y creo un nuevo objeto con el cubo

                    cube=cube-(0,0.05,0)
        
        cv.imshow('source',frame)
                  
    
    

