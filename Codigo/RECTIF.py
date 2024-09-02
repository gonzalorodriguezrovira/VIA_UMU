#https://github.com/gonzalorodriguezrovira/VIA_UMU

import cv2 as cv
import numpy as np
import numpy.linalg      as la
from umucv.util import putText
from umucv.stream import autoStream
from collections import deque

medidor = deque(maxlen=2)#Variable para contener los dos puntos con los que quiero medir
medidor3 = deque(maxlen=2)#Variable para contener los dos puntos con los que quiero medir
points = deque()#Variable para contener los puntos para marcar el objeto de referencia

def homog(x):
    ax = np.array(x)
    uc = np.ones(ax.shape[:-1]+(1,))
    return np.append(ax,uc,axis=-1)

def inhomog(x):
    ax = np.array(x)
    return ax[..., :-1] / ax[...,[-1]]

def htrans(h,x):
    return inhomog(homog(x) @ h.T)

def funFrame(event, x, y, flags, param):#Funcion para obtener valores al hacer cicl en mi frame
    if event == cv.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
        else:
            medidor.append((x, y))

def funRec(event, x, y, flags, param):#Funcion para obtener valores al hacer cicl en mi imagen rectificada
    if event == cv.EVENT_LBUTTONDOWN:
        if len(points) == 4:
            medidor3.append((x,y))
    
def readFile(fichero):#Funcion para leer de un archivo los datos de la medidas totales
    with open(fichero, 'r') as f:
        lineas = f.readlines()
        lista = []
        for l in lineas:
            elementos = map(float, l.strip().split())
            lista.append(tuple(elementos))
    return lista

cv.namedWindow("rec")#Declaro los frames y les asocio la funcion fun para el clik
cv.setMouseCallback("rec", funRec)
cv.namedWindow("frame")
cv.setMouseCallback("frame", funFrame)

medidas=readFile("datos.txt")#Obtengo las medidas

real = np.array([#Posicion con medidas reales escalas para el tamaño de mi frame donde esta la imagen escalada
    [  400.,   (200+(medidas[0])[1]*12)],
    [ (400+(medidas[0])[0]*12),   (200+(medidas[0])[1]*12)],
    [ (400+(medidas[0])[0]*12),  200.],
    [  400.,  200.]])

for key, frame in autoStream():#Esta en el bucle ya que es diseñado para que se le pase una referencia por --dev=dir:...., por eso es necesario que la impresión de los cuatro puntos fijos se realice en el bucle
    if key == ord('x'):#Borro todo tanto las seleccion de objeto como mis medidas
        
        points.clear()
        medidor.clear()
    
    for p in points:
        
        cv.circle(frame, p,3,(0,255,0),-1)#Dibujo todos los puntos que seleccionan mi objeto
        
        if len(points) == 4:#En caso de ser 4 ya puedo tener el objeto medido ya que supongo que todos los objetos serán de 4 lados
            
            points2=np.array([[(points[0])[0],(points[0])[1]],[(points[1])[0],(points[1])[1]],[(points[2])[0],(points[2])[1]],[(points[3])[0],(points[3])[1]]])#Transformo             mis puntos seleccionados en un np.array
            H,_ = cv.findHomography(points2, real)
            rec = cv.warpPerspective(frame,H,(600,600))#Creo mi frame rectificado con mi matriz
            rec=cv.rotate(cv.flip(rec, 0), cv.ROTATE_90_CLOCKWISE)#Coloco la orientacion correcta a la referencia D
            
            d1 = np.linalg.norm(np.array(points[1])-points[0])#Calculo las medidas de mis puntos seleccionados
            d2= np.linalg.norm(np.array(points[2])-points[1])
            d3= np.linalg.norm(np.array(points[3])-points[2])
            d4= np.linalg.norm(np.array(points[0])-points[3])
            
            cv.line(frame, points[0],points[1],(0,255,0))#Dibujo para mi figura su medida tanto en pixeles como en cm en su linea 
            c = np.mean((points[0],points[1]), axis=0).astype(int)
            putText(frame,f'{d1:.1f} pix//{(medidas[0])[0]}cm',c)
            cv.line(frame, points[1],points[2],(0,255,0))
            c = np.mean((points[1],points[2]), axis=0).astype(int)
            putText(frame,f'{d2:.1f} pix//{(medidas[0])[1]}cm',c)
            cv.line(frame, points[2],points[3],(0,255,0))
            c = np.mean((points[2],points[3]), axis=0).astype(int)
            putText(frame,f'{d3:.1f} pix//{(medidas[1])[0]}cm',c)
            cv.line(frame, points[3],points[0],(0,255,0))
            c = np.mean((points[3],points[0]), axis=0).astype(int)
            putText(frame,f'{d4:.1f} pix//{(medidas[1])[1]}cm',c)
            
            pointsr = htrans(H,points)
            d1r = np.linalg.norm(np.array(pointsr[1])-pointsr[0])#Calculo la escala de pix por cm para mi normalizado
            d2r= np.linalg.norm(np.array(pointsr[2])-pointsr[1])
            d3r= np.linalg.norm(np.array(pointsr[3])-pointsr[2])
            d4r= np.linalg.norm(np.array(pointsr[0])-pointsr[3])
            prop1r=d1r/(medidas[0])[0]
            prop2r=d2r/(medidas[0])[1]
            prop3r=d3r/(medidas[1])[0]
            prop4r=d4r/(medidas[1])[1]
            propr=np.mean((prop1r,prop2r,prop3r,prop4r))
        
            for p in medidor3:#Muestro mis puntos de medicion
                
                cv.circle(rec, p,3,(0,0,255),-1)
                
                if len(medidor3) == 2:#Cuando son dos dibujo una linea y la informacion de su medida
                    
                    cv.line(rec,medidor3[0],medidor3[1],(0,0,255))
                    c = np.mean(medidor3, axis=0).astype(int)
                    d= np.linalg.norm(np.array(medidor3[0])-medidor3[1])
                    putText(rec,f'{d/propr:.1f} cm',c)#Calculo su distancia respecto a la proporcion
                 
            for p in medidor:#Muestro mis puntos de medicion
                
                cv.circle(frame, p,3,(255,0,0),-1)
                
                if len(medidor) == 2:#Cuando son dos dibujo una linea y la informacion de su medida
                    
                    cv.line(frame,medidor[0],medidor[1],(255,0,0))
                    c = np.mean(medidor, axis=0).astype(int)
                    aux=htrans(H,medidor)#Normalizo mis puntos de medicion
                    d= np.linalg.norm(np.array(aux[0])-aux[1])
                    putText(frame,f'{d/propr:.1f} cm',c)#Calculo su distancia respecto a la proporcion
           
            cv.imshow('rec',rec)#La muestro de manera que esta bien orientada 
    
    cv.imshow('frame',frame)
    
cv.destroyAllWindows()