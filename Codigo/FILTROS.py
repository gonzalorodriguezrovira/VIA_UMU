#!/usr/bin/env python

# > ./stream.py
# > ./stream.py --dev=help
#https://github.com/gonzalorodriguezrovira/VIA_UMU


import cv2   as cv
import numpy as np
import time 

from umucv.stream import autoStream
from umucv.util import ROI, putText
from umucv.util import Help

def mytrackbar(param,window,x,a,b):#Funcion para colocar trackbar en una ventana
    def fun(v):
        x[0]=v*(b-a)/100+a
    cv.createTrackbar(param,window,int((x[0]-a)*100/(b-a)),100,fun)
    
help = Help(#Menu de ayuda
"""
BLUR FILTERS

0: do nothing
1: Box
2: Gaussian
3: Diferencia
4: Premask
5: Mask
6: Masked

c: color/monochrome
r: only roi
m: fijar region

h: show/hide help
""")

color=True#Varaiable para controlar si se usa blanco y negro o color 
roi=False#Variable para controlar si ya ha sido marcada la zona del filtro
todo=False#Variable de control para saber si aplicacar el filtro en toda la ventana o solo en una seccion
seleccionado=False#Varaibles para el control de la actividad de los filtros
seleccionado1=False
seleccionado2=False
seleccionado3=False
seleccionado4=False
seleccionado5=False
seleccionado6=False

    
cv.namedWindow("input")#Inicializo mi ventana
region = ROI("input")#Inicializo mi seleccion sobre la ventana ya creada

SIGMA=[3]
B=[50]
B2=[30]
H=[0.3]

mytrackbar('SIGMA','input',SIGMA,1,10)#Coloco todas mis trackbars y las asocio a su lista 
mytrackbar('B','input',B,1,100)
mytrackbar('B2','input',B2,1,100)
mytrackbar('H','input',H,0,1)

for key,frame in autoStream():
    
    if key == ord('0'):#En caso de pulsar 0 se quitara el filtro activo
        
        seleccionado=False
        seleccionado1=False
        seleccionado2=False
        seleccionado3=False
        seleccionado4=False
        seleccionado5=False
        seleccionado6=False
        
    if key == ord('r'):#En caso de pulsar r el flitro se aplicara a toda la ventana o a la region ya seleccionada
        
        todo=not todo
    
    help.show_if(key, ord('h'))#Monstrar menu de ayuda
    
    if region.roi or todo:#Solo se monstraran los filtros si tengo o bien una region seleccionada donde aplicarlo o bien estoy aplicando el fultro en toda mi ventana
        
        frameTodo=frame#Inicializo el frame que monstrará tanto el frame original como la zona con un filtro
         
        if not roi and not todo:#En el caso de que aun no tenga seleccionado mi region y no estar en el modo de toda la pantalla
            
            [x1,y1,x2,y2] = region.roi #Obtengo los valores de mi sección 
                    
        if key == ord('m'):#Confirmo que quiero esa sección para aplicar los filtros
            
            roi=True
        
        if key == ord('c'):#Intercambio entre color y blanc y negro
            
            color= not color

        if not color:
            
            result = cv.cvtColor(frame,cv.COLOR_RGB2GRAY)#Transformo mi imagen a color en blanco y negro
            result = cv.cvtColor(result,cv.COLOR_GRAY2RGB)#Para seguir teniendo tres canales y poder sustituir en mi imagen a color una imagen en blanco y negro debo volverla a RGB para tener 3 canales
            if roi:#En caso de tener una seccion ya seleccionada
                frame[y1:y2+1, x1:x2+1]=result[y1:y2+1, x1:x2+1]#Reenplazo la seccion por ella misma en blanco y negro
            
        else:
            
            result = frame#En caso de ser a color mantengo mi frame en result
         
        if todo: #En caso de estar aplicando los filtros en la ventana entera le asigno result ya que indicara si mantengo color o blanco y negro
            
                frameTodo=result
                
        #Creacion de filtro 2
        t1 = time.time()
        smooth = cv.GaussianBlur(result,(0,0),SIGMA[0])
        t2=time.time()
        putText(smooth,f'sigma={SIGMA[0]:.1f}')
        putText(smooth,f'{1000*(t2-t1):5.1f}ms',orig=(5,35))
        
        if key == ord('2') and not seleccionado: #En caso de querer activar el filtro 2 y no tener otro activo
            
            seleccionado2=not seleccionado2#Indico que selecciono el filtro 2
            seleccionado= not seleccionado#Indico que hay un filtro activo

        if seleccionado2:#En caso de tener el filtro seleccionado
            
            if todo:#En caso de aplicarse a toda la ventana
                
                frameTodo=cv.addWeighted(result,0,smooth,1,0)#Le doy una mayor prioridad a smooth para que se muestre
                
            else:#En caso de aplicarse solo a la zona seleccionada
                
                frame[y1:y2+1, x1:x2+1]=smooth[y1:y2+1, x1:x2+1]#Coloco la parte seleccionada de smooth en mi frame original
        
        #Creacion de filtro 1
        t1 = time.time()
        sz=int(B[0])
        box=cv.boxFilter(result,-1,(sz,sz))
        t2=time.time()

        putText(smooth,f"sigma={SIGMA[0]:.1f}")
        putText(smooth,f'{1000*(t2-t1):5.1f}ms',orig=(5,35))  

        if key == ord('1')and not seleccionado:#En caso de querer activar el filtro 1 y no tener otro activo
            
            seleccionado1=not seleccionado1#Indico que selecciono el filtro 1
            seleccionado= not seleccionado#Indico que hay un filtro activo

        if seleccionado1:#En caso de tener el filtro seleccionado
            
            if todo:#En caso de aplicarse a toda la ventana
                
                frameTodo=cv.addWeighted(result,0,box,1,0)#Le doy una mayor prioridad a box para que se muestre
                
            else:#En caso de aplicarse solo a la zona seleccionada
                
                frame[y1:y2+1, x1:x2+1]=box[y1:y2+1, x1:x2+1]#Coloco la parte seleccionada de box en mi frame original
        
        #Creacion de filtro 3
            
        dif =cv.absdiff(result,box)

        if key == ord('3')and not seleccionado:#En caso de querer activar el filtro 3 y no tener otro activo
            
            seleccionado3=not seleccionado3#Indico que selecciono el filtro 3
            seleccionado= not seleccionado#Indico que hay un filtro activo

        if seleccionado3:#En caso de tener el filtro seleccionado
            if todo:#En caso de aplicarse a toda la ventana
                
                frameTodo=cv.addWeighted(result,0,dif,1,0)#Le doy una mayor prioridad a dif para que se muestre
                
            else:#En caso de aplicarse solo a la zona seleccionada
                
                frame[y1:y2+1, x1:x2+1]=dif[y1:y2+1, x1:x2+1]#Coloco la parte seleccionada de dif en mi frame original

        #Creacion de filtro 4
        
        sz2 = int(B2[0])
        premask=cv.boxFilter(dif,-1,(sz2,sz2))

        if key == ord('4')and not seleccionado:#En caso de querer activar el filtro 4 y no tener otro activo
            
            seleccionado4=not seleccionado4#Indico que selecciono el filtro 4
            seleccionado= not seleccionado#Indico que hay un filtro activo

        if seleccionado4:#En caso de tener el filtro seleccionado
            
            premask=premask*6
            
            if todo:#En caso de aplicarse a toda la ventana
                
                frameTodo=cv.addWeighted(result,0,premask,1,0)#Le doy una mayor prioridad a premask para que se muestre
                
            else:#En caso de aplicarse solo a la zona seleccionada
                
                frame[y1:y2+1, x1:x2+1]=premask[y1:y2+1, x1:x2+1]#Coloco la parte seleccionada de premask en mi frame original

        #Creacion de filtro 5
        
        mask=premask>H[0]

        if key == ord('5')and not seleccionado:#En caso de querer activar el filtro 5 y no tener otro activo
            
            seleccionado5=not seleccionado5#Indico que selecciono el filtro 5
            seleccionado= not seleccionado#Indico que hay un filtro activo

        if seleccionado5:#En caso de tener el filtro seleccionado

            if todo:#En caso de aplicarse a toda la ventana
                
                mask=mask.astype(float)
                frameTodo=cv.addWeighted(result,0,mask,1,0, dtype = cv.CV_32F)#Le doy una mayor prioridad a mask para que se muestre 
                
            else:#En caso de aplicarse solo a la zona seleccionada
                
                frame[y1:y2+1, x1:x2+1]=mask[y1:y2+1, x1:x2+1]#Coloco la parte seleccionada de mask en mi frame original

        #Creacion de filtro 6
        
        masked = frame.copy()
        masked[mask==False]=0

        if key == ord('6')and not seleccionado:#En caso de querer activar el filtro 6 y no tener otro activo
            
            seleccionado6=not seleccionado6#Indico que selecciono el filtro 6
            seleccionado= not seleccionado#Indico que hay un filtro activo

        if seleccionado6:#En caso de tener el filtro seleccionado

            if todo:#En caso de aplicarse a toda la ventana
                
                frameTodo=cv.addWeighted(result,0,masked,1,0, dtype = cv.CV_32F)#Le doy una mayor prioridad a masked para que se muestre
                
            else:#En caso de aplicarse solo a la zona seleccionada
                
                frame[y1:y2+1, x1:x2+1]=masked[y1:y2+1, x1:x2+1]#Coloco la parte seleccionada de masked en mi frame original

         
        if not roi and not todo:#Una vez ya tengo seleccionado mi roi o bien voy a aplicar el filtro en toda la ventana no muestro los bordes de mi region
            
            cv.rectangle(frame, (x1,y1), (x2,y2), color=(0,255,0), thickness=2)#Dibujo el rectangulo de la zona seleccionada
    
    if todo:#En caso de aplicar filtros en toda la ventana muestro el frame que contiene la aplicacion de filtros a toda la imagen
        
        cv.imshow('input',frameTodo)
        
    else:#En caso de que solo se apliquen a una seccion muestro el frame que tiene la seccion sustituida por el filtro
        
        cv.imshow('input',frame)
    
    
cv.destroyAllWindows()