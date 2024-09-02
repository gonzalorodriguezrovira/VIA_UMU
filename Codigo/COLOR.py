#https://github.com/gonzalorodriguezrovira/VIA_UMU

import cv2 as cv
import numpy as np

from umucv.stream import autoStream
from umucv.util import putText


seleccionado =False#Valor de control para saber en que fase me encuentro

colors = []# Lista para almacenar los colores seleccionados
kernel = np.ones((5,5), np.uint8)


def seleccionaColor(event, x, y, flags, param):#Función de callback del mouse para obtener los colores

    if event == cv.EVENT_LBUTTONUP:
            hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)# Obtengo el valor HSV de cada pixel seleccionado
            colors.append(hsv[y,x])#Añado ese valor a mis lista de colores

cv.namedWindow("frame")
cv.setMouseCallback("frame", seleccionaColor)            

for key, frame in autoStream():
       
    if not seleccionado:#Parte de seleccionado 
 
        cv.imshow('frame', frame)
        frame2=frame#Guardo el frame original para el caso de que quiera seleccionar un nuevo colo vuelva a la original antes de realizar los
                    #tres click en un nuevo tono

        hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)#Convierto la imagen a HSV
        
        if len(colors) == 3:#Mientras muestro la  imagen  esperaro a que los colores sean seleccionados, cuando sean seleccionados paso
                            #a la parte de  buscar y dibujar los contronos de estos
            seleccionado= True
                        
    if seleccionado:#Parte buscado y dibujado de contornos     
        
        mean_color = np.mean(colors, axis=0) #Calculo la media de los valores HSV de los colores seleccionados
        lower_color = np.array([mean_color[0]-10, mean_color[1]-50, mean_color[2]-50]) #Defino el rango, límites superiores e inferiores de rango de color en HSV
        upper_color = np.array([mean_color[0]+10, mean_color[1]+50, mean_color[2]+50])   

        mask = cv.inRange(hsv_frame, lower_color, upper_color)#Aplico la máscara a la imagen 
        opening = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)#Operación para eliminar pequeños objetos no deseados        
        contours, hierarchy = cv.findContours(opening, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)#busco los contornos de los objetos en la máscara

        cv.drawContours(frame, contours, -1, (0,255,0), 3)#Dibujo los contornos encontrados sobre el frame original con el mismo tono de color
        putText(frame, f'{len(contours)} objetos')#Muestro el numero de objetos encontrados del mismo tono
        
        if key == ord('x'):#En caso de que seleccione un nuevo tono 
            
            seleccionado=False#Indico que debo volver a la patr de seleccion
            colors.clear()#Vacio todos los colores
            frame=frame2#Vuelvo a mi frame sin los contronos dibujados
            
        cv.imshow('frame', frame)

cv.destroyAllWindows()