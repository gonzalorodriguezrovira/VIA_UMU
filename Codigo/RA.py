#https://github.com/gonzalorodriguezrovira/VIA_UMU

import cv2          as cv
import numpy        as np

from umucv.stream   import autoStream
from umucv.htrans   import htrans, Pose
from umucv.util     import cube, showAxes
from umucv.contours import extractContours, redu

destino=()#Variable que contine la posicion a la que debe llegar el cubo 
posicion=()#Variable que contine la posicion en la que se situa el cubo

def fun(event, x, y, flags, param):
    global destino
    if event == cv.EVENT_LBUTTONDOWN:
        destino=(x,y)
        
def Kfov(sz,hfovd):
    hfov = np.radians(hfovd)
    f = 1/np.tan(hfov/2)
    w,h = sz
    w2 = w / 2
    h2 = h / 2
    return np.array([[f*w2, 0,    w2],
                     [0,    f*w2, h2],
                     [0,    0,    1 ]])

cv.namedWindow("source")
cv.setMouseCallback("source", fun)

stream = autoStream()

HEIGHT, WIDTH = next(stream)[1].shape[:2]
size = WIDTH,HEIGHT

K = Kfov( size, 60 )

marker = np.array(
       [[0,   0,   0],
        [0,   1,   0],
        [0.5, 1,   0],
        [0.5, 0.5, 0],
        [1,   0.5, 0],
        [1,   0,   0]])

square = np.array(
       [[0,   0,   0],
        [0,   1,   0],
        [1,   1,   0],
        [1,   0,   0]])

def polygons(cs,n,prec=2):
    rs = [ redu(c,prec) for c in cs ]
    return [ r for r in rs if len(r) == n ]

def rots(c):
    return [np.roll(c,k,0) for k in range(len(c))]

def bestPose(K,view,model):
    poses = [ Pose(K, v.astype(float), model) for v in rots(view) ]
    return sorted(poses,key=lambda p: p.rms)[0]

for n, (key,frame) in enumerate(stream):
   
    g = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    cs = extractContours(g, minarea=5, reduprec=2)
    good = polygons(cs,6,3)
    poses = []
    
    for g in good:
        p = bestPose(K,g,marker)
        if p.rms < 2:
            poses += [p.M]
            
    if poses:#Para este ejercicio solo necesito una pose de referencia por lo que al tener una ya podré actuar
        
        M=poses[0]#Me quedo con la primera pose ya que solo necesito actuar sobre una

        x,y = htrans(M, (0.7,0.7,0) ).astype(int)#Capturamos el color de un punto cerca del marcador para borrarlo
        b,g,r = frame[y,x].astype(int)
        cv.drawContours(frame,[htrans(M,marker).astype(int)], -1, (0,0,0) , 3, cv.LINE_AA)#Dibujando un cuadrado encima

        showAxes(frame, M, scale=0.5)# Mostramos el sistema de referencia inducido por el marcador

        cosa = (cube)* (0.5, 0.5, 0.5)#Creo mi cubo 
        
        posicion=[ htrans(M, cosa).astype(int) ][0][0]#Obtengo la posicion de mi cubo 
        
        if destino:#Si se ha marcado un punto al que ir me desplazo
            
            if destino[0]==posicion[0]+2 or destino[0]==posicion[0]-2:#Muchas veces el cubo no llega a la posicion exacta, para solucionar eso hago una aproximacion
                posicion[0]=destino[0]
                
            if destino[1]==posicion[1]+2 or destino[1]==posicion[1]-2:
                posicion[1]=destino[1]
                
            if destino[0]!=posicion[0]:#Trato si no se encuentra el cubo en su eje x 
                
                if(posicion[0]<destino[0]):#En caso de ser mi x menor a la del destino la aumento y creo un nuevo objeto con el cubo
            
                    cube=cube+(0.05,0,0)
                    cosa2 = (cube)* (0.5, 0.5, 0.55 + 0.2 * np.sin(n / 50))
                    posicion2=[ htrans(M, cosa2).astype(int) ][0][0]#Creo esta variable para obtener de nuevo la posicion del cubo y comprobar que el movimiento se ha realizado en el sentido correcto ya que en ocasiones cuando tratamos con camaras que rotan y alteran el valor de x produce un fallo por lo que de esta manera se donde se ha trasladado mi cubo
                    
                    if(posicion2[0]<posicion[0]):#Compruebo que mi cubo se ha trasladado en el sentido correcto
                        
                        cube=cube-(0.1,0,0)#Si no es asi lo desplazo el doble en el otro sentido para compensar el desplazamiento erroneo anterior

                elif(posicion[0]>destino[0]):#En caso de ser mi x mayor a la del destino la reduzco y creo un nuevo objeto con el cubo
                    
                    cube=cube-(0.05,0,0)
                    cosa2 = (cube)* (0.5, 0.5, 0.55 + 0.2 * np.sin(n / 50))
                    posicion2=[ htrans(M, cosa2).astype(int) ][0][0]#Creo esta variable para obtener de nuevo la posicion del cubo y comprobar que el movimiento se ha realizado en el sentido correcto ya que en ocasiones cuando tratamos con camaras que rotan y alteran el valor de x produce un fallo por lo que de esta manera se donde se ha trasladado mi cubo
                    
                    if(posicion2[0]>posicion[0]):#Compruebo que mi cubo se ha trasladado en el sentido correcto
                        
                        cube=cube+(0.1,0,0)#Si no es asi lo desplazo el doble en el otro sentido para compensar el desplazamiento erroneo anterior

            if destino[1]!=posicion[1]:#Trato si no se encuentra el cubo en su eje y

                if(posicion[1]<destino[1]):#En caso de ser mi y menor a la del destino la aumento y creo un nuevo objeto con el cubo
                    
                    cube=cube+(0,0.05,0)
                    cosa2 = (cube)* (0.5, 0.5, 0.55 + 0.2 * np.sin(n / 50))
                    posicion2=[ htrans(M, cosa2).astype(int) ][0][0]#Creo esta variable para obtener de nuevo la posicion del cubo y comprobar que el movimiento se ha realizado en el sentido correcto ya que en ocasiones cuando tratamos con camaras que rotan y alteran el valor de y produce un fallo por lo que de esta manera se donde se ha trasladado mi cubo
                    
                    if(posicion2[1]<posicion[1]):#Compruebo que mi cubo se ha trasladado en el sentido correcto
                        
                        cube=cube-(0,0.1,0)#Si no es asi lo desplazo el doble en el otro sentido para compensar el desplazamiento erroneo anterior

                elif(posicion[1]>destino[1]):#En caso de ser mi y mayor a la del destino la reduzco y creo un nuevo objeto con el cubo
                    
                    cube=cube-(0,0.05,0)
                    cosa2 = (cube)* (0.5, 0.5, 0.55 + 0.2 * np.sin(n / 50))
                    posicion2=[ htrans(M, cosa2).astype(int) ][0][0]#Creo esta variable para obtener de nuevo la posicion del cubo y comprobar que el movimiento se ha realizado en el sentido correcto ya que en ocasiones cuando tratamos con camaras que rotan y alteran el valor de x produce un fallo por lo que de esta manera se donde se ha trasladado mi cubo
                    
                    if(posicion2[1]>posicion[1]):#Compruebo que mi cubo se ha trasladado en el sentido correcto
                        
                        cube=cube+(0,0.1,0)#Si no es asi lo desplazo el doble en el otro sentido para compensar el desplazamiento erroneo anterior
                        
        cv.drawContours(frame, [ htrans(M, cosa).astype(int) ], -1, (0,128,0), 3, cv.LINE_AA)#Dibujo el cubo

    cv.imshow('source',frame)
    
