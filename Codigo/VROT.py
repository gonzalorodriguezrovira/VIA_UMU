#!/usr/bin/env python
#https://github.com/gonzalorodriguezrovira/VIA_UMU

import cv2 as cv
import numpy as np
import time

from umucv.stream import autoStream, sourceArgs
from umucv.util import putText

FOVH = 52.47 #Constantes de FOV del ejercicio1
FOVV = 66.575

tracks = []
track_len = 20
detect_interval = 5
tH=0#Variables para ir actualizando el total de angulo desplazado horizontal y vertical
tV=0
vectorP = np.array([0, 0], dtype=np.float32) #Inicializo un vector bidimensional para cada uno de mis ejes 


corners_params = dict(maxCorners=500,
                      qualityLevel=0.1,
                      minDistance=10,
                      blockSize=7)

lk_params = dict(winSize=(15, 15),
                 maxLevel=2,
                 criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))



for n, (key, frame) in enumerate(autoStream()):
    
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    t0 = time.time()
    
    if len(tracks):
        
        # el criterio para considerar bueno un punto siguiente es que si lo proyectamos
        # hacia el pasado, vuelva muy cerca del punto incial, es decir:
        # "back-tracking for match verification between frames"
        
        p0 = np.float32([t[-1] for t in tracks])
        p1, _, _ = cv.calcOpticalFlowPyrLK(prevgray, gray, p0, None, **lk_params)
        p0r, _, _ = cv.calcOpticalFlowPyrLK(gray, prevgray, p1, None, **lk_params)
        d = abs(p0 - p0r).reshape(-1, 2).max(axis=1)
        good = d < 1
        new_tracks = []
        totalDesplazado = np.array([0, 0], dtype=np.float32)#Inicializo mi varaible como un vector de dos dimensiones para llevar el total desplazado de mis dos ejes
        numDesplazados = 0 #Inicializo el total de desplazados
        
        for t, (x, y), ok in zip(tracks, p1.reshape(-1, 2), good):
            
            if not ok:
                
                continue
                
            t.append([x, y])
            
            if len(t) > track_len:
                
                del t[0]
            new_tracks.append(t)
            totalDesplazado += np.array([x, y], dtype=np.float32) - np.array(t[-2], dtype=np.float32)#Por cada punto de seguimiento válido actualizo el desplazamiento sumandolo
            numDesplazados+=1 #Lo aumento en uno por cada punto de seguimiento válido

        tracks = new_tracks
        
        if numDesplazados > 0:#Despues de procesar todos los puntos de seguimiento calculo el vector medio de desplazamiento
            
            vectorP = totalDesplazado / numDesplazados

        cv.polylines(frame, [np.int32(t) for t in tracks], isClosed=False, color=(0, 0, 255))
        
        for t in tracks:
            
            x, y = np.int32(t[-1])
            cv.circle(frame, (x, y), 2, (0, 0, 255), -1)

    t1 = time.time()#Reseteo el tracking
    dt = t1 - t0#Me quedo la diferencia de tiempos ya que la necesito para poder calcular la velocidad y los angulos de la camara

    if n % detect_interval == 0:
        
        # Creamos una máscara para indicar al detector de puntos nuevos las zona
        # permitida, que es toda la imagen, quitando círculos alrededor de los puntos
        # existentes (los últimos de las trayectorias).
        
        mask = np.zeros_like(gray)
        mask[:] = 255
        
        for x, y in [np.int32(t[-1]) for t in tracks]:
            
            cv.circle(mask, (x, y), 5, 0, -1)
            
        corners = cv.goodFeaturesToTrack(gray, mask=mask, **corners_params)
        
        if corners is not None:
            
            for [(x, y)] in np.float32(corners):
                
                tracks.append([[x, y]])

    putText(frame, f'{len(tracks)} corners, {(t1 - t0) * 1000:.0f}ms')
    centro = (frame.shape[1] // 2, frame.shape[0] // 2)#Calculo el centro de mi frame
    vectorAumentado = vectorP * 5  # Ampliado y en dirección opuesta
    final = tuple(np.int32(np.array(centro) + vectorAumentado))#Calculo hasta donde debe llegar
    cv.arrowedLine(frame, centro, final, (0, 165, 255), 2) #Creo mi flecha que ira en sentido contrario al movimiento
    width, height = frame.shape[1], frame.shape[0] #Saco el ancho y la altura de mi frame
    vectorPDeg = vectorP * np.array([FOVH / width, FOVV / height], dtype=np.float32)#Variable que almacena el vector medio de desplazamiento en grados
    
    if not np.isnan(vectorPDeg).any()and not np.isnan(dt):#Compruebo que mis valores no son nulos 
        
        vectorPDegS = vectorPDeg / dt#Variable que almacena el vector medio de desplazamiento en grados por segundo
        vH=vectorPDegS[0]#Saco la velocidad correspondiente a cada eje 
        vV=vectorPDegS[1]
        if not np.isnan(vectorPDegS[0]*dt) and not np.isnan(vectorPDegS[1]*dt): #Por algun motivo en algunos giros daba valores NaN que rompia toda la acumulación asi que debo tratarlo
            tH+=vectorPDegS[0]*dt#Acumulo para cada eje el total desplazado
            tV+=vectorPDegS[1]*dt
            putText(frame,f'Velocidad de giro: {vH:.2f}grados/s (horizontal), {vV:.2f}grados/s (vertical)',orig=(5,36), color=(200,255,200))#Coloco en el frame mi velocidad de giro en ambos ejers
            putText(frame,f'Total de giro: {tH:.2f}grados (horizontal), {tV:.2f}grados (vertical)',orig=(5,58), color=(255,200,200))#Coloco en el frame el total de rotacion acumulado en ambos ejers
    
    cv.imshow('input', frame)
    prevgray = gray

