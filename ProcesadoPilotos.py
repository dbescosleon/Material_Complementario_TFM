# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 09:42:04 2022

@author: jmbelda
"""

from read_OpenSignals import read_OpenSignals
from glob import glob

#%%

# ruta = r'G:\Mi unidad\Revisor\Tesis\EnaBula\Sujetos\*.txt'

# Esta es la ruta de acceso desde mi ordenador
ruta = r'G:\.shortcut-targets-by-id\1Jr79_0v1vYYbcpKgFRS6Ax1eprhvTfOm\Sujetos\*.txt'

ficheros = glob(ruta)


#%%
from scipy.signal import butter, filtfilt
from numpy import array, abs
from matplotlib.backends import backend_pdf
import matplotlib.pyplot as plt


fs = 1000
hfs = fs/2

# Filtros a usar
filtros = {"tendencia" : butter(4, 0.04/hfs, 'high'),
           "50 Hz"     : butter(4, array([48, 52])/hfs, 'bandstop'),
           "envolvente": butter(4, 2/hfs)}




with backend_pdf.PdfPages("./salidas.pdf") as pdf:
    for f in ficheros:
        sennal, header = read_OpenSignals(f)
        
        emg = array(sennal["EMGmV"])
        tiempo = array(sennal.index)
        
        # Quitamos la tendencia
        femg = filtfilt(filtros["tendencia"][0],
                        filtros["tendencia"][1],
                        emg)
        
        # Quitamos el ruido
        femg = filtfilt(filtros["50 Hz"][0],
                        filtros["50 Hz"][1],
                        femg)
        
        # Sacamos la envolvente
        env_emg = filtfilt(filtros["envolvente"][0],
                           filtros["envolvente"][1],
                           abs(femg))
        
        myfig, ax = plt.subplots(2, 1, tight_layout=True)
        
        ax[0].plot(tiempo, emg)
        ax[0].set_title(f.split('\\')[-1])
        
        ax[1].plot(tiempo, env_emg)
        ax[1].set_xlabel("Time (s)")
        
        pdf.savefig(myfig)
        plt.close(myfig)


