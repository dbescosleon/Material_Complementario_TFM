# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 17:09:19 2021

@author: jmbelda
"""

import pandas as pd
import ast
import re


def read_OpenSignals(fname, sensors=True):
    
    info_header = {}
    
    with open(fname) as fid:
        cab = fid.readline()
        
        if 'OpenSignals' not in cab: raise Exception("Wrong file format")
        
        header = True
        
        while header:
            cab = fid.readline()
            
            if "{" in cab:
                info_header = ast.literal_eval(cab[2:])
            elif "EndOfHeader" in cab:
                header = False
                
        data = pd.read_csv(fid, sep="\t", header=None)
        
    dev = list(info_header.keys())[0]
    header = info_header[dev]
    
    if data.shape[1] != len(header['column']):
        cols = list(data.keys())[:-1]
        data = data[cols]
        
        
    columns = header['column']
    
    if sensors:
        nSensors = len(header['sensor'])
        columns[-nSensors:] = header['sensor']
        
    
    # Setting-up columns names
    data.columns = header['column']
    
    # If sensors, callibrating sensors
    if sensors:
        columnas = list(data.columns)
        
        for c, s in enumerate(columnas):
            if 'EDA' in s:
                data[s] = EDA2uS(data[s])
                
                # Cambiamos el nombre
                numeros = ''.join([z for z in columnas[c] if z.isdigit()])
                columnas[c] = "EDAuS"+numeros
                
            elif 'EMG' in s:
                data[s] = EMG2mV(data[s])

                # Cambiamos el nombre
                numeros = ''.join([z for z in columnas[c] if z.isdigit()])
                columnas[c] = "EMGmV"+numeros
            elif 'ECG' in s:
                data[s] = ECG2mV(data[s])

                # Cambiamos el nombre
                numeros = ''.join([z for z in columnas[c] if z.isdigit()])
                columnas[c] = "ECGmV"+numeros
        
        data.columns = columnas
                
        data.index /= header['sampling rate']
    
    return data, header



n = 10 # Bits, aunque también pueden ser 6
Vcc = 3.3 # V  (1.8 - 5.5)V
    

def EDA2uS(Valor):
    '''
    Converts bits to uSiemens

    Parameters
    ----------
    Valor : float, array
        The EDA values from BITALINO.

    Returns
    -------
    EDA : array
        The EDA values in uSiemens.

    '''
    
    EDA = ((Valor/(2**n))*Vcc)/0.12
    
    return EDA



def ECG2mV(Value):
    
    ECG = (Value * Vcc / (2**n) - (Vcc / 2))
    
    return ECG

def EMG2mV(Value):
    EMG = (Value * Vcc / (2**n) - (Vcc / 2))

    return EMG

'''
https://forum.bitalino.com/viewtopic.php?t=128

EMG [-1.65 mV : 1.65 mV]

EMGV = (EMGB * Vcc / 2^n - Vcc / 2) / GEMG
EMGmV = EMGV * 1000

Where:
EMGV – EMG value in Volts (V)
EMGmV - EMG value in miliVolts (mV)
EMGB – EMG value obtained from BITalino
Vcc – Operating Voltage (V)
n – number of bits (bit)
GEMG – EMG Sensor Gain

Values:
Vcc = 3.3 (V)
GEMG = 1000
n = See Number of Bits section

ECG [-1.5 mV : 1.5 mV]

ECGV = (ECGB * Vcc / 2^n - Vcc / 2) / GECG
ECGmV = ECGV * 1000

Where:
ECGV – ECG value in Volts (V)
ECGmV - ECG value in miliVolts (mV)
ECGB – ECG value obtained from BITalino
Vcc – Operating Voltage (V)
n – number of bits (bit)
GECG – ECG Sensor Gain

Values:
Vcc = 3.3 (V)
GECG = 1100
n = See Number of Bits section

EDA [1 µS : ∞ µS]

RMOhm = 1 - EDAB / 2^n
EDAµS = 1 / RMOhm

Where:
EDAµS – EDA value in micro Siemens (µS)
EDAB – EDA value obtained from BITalino
RMOhm - Sensor resistance in megaOhms(MOhm)
n – number of bits (bit)

Values:
n = See Number of Bits section

ACC [-3 g : 3 g]

ACCg = 2 * ((ACCB - Cm) / (CM - Cm)) - 1

Where:
ACCg – ACC value in g-force (g)
ACCB – ACC value obtained from BITalino
Cm – Calibration Value (Minimum)
CM – Calibration Value (Maximum)

Values:
Cm* = 208
CM* = 312

*Cm and CM may be calculated by slow rotation of the board (or accelerometer itself) to force the accelerometer’s axis to rotate 360º.
'''