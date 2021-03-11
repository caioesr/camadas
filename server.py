# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 18:26:52 2021

@author: caioe
"""

from enlace import *
import time
import numpy as np
from tkinter import filedialog, Tk
import sys
import time

serialName = "COM4"
header_size = 3

def main(dirname, filename):
    try:
        com1 = enlace(serialName)
        com1.enable()
        
        print('Recepcao de dados comecando...')
        
        imgW = f'{dirname}\{filename}'
        header, nHeader = com1.getData(header_size)
        txLen = int.from_bytes(header, 'big')
        
        rxBuffer, nRx = com1.getData(txLen)
        
        end = time.time()
        start = open('history.txt','r').read()
        
        f = open(imgW,'wb')
        f.write(rxBuffer)
        f.close()
        
        print(f"Recebeu {nRx} bytes")
        print(f"Baud rate = {nRx/(end-float(start))}")
            
    
        # Encerra comunicação
        print("\n\nComunicação encerrada")
        
        com1.disable()
    
    except Exception as erro:
        #print("ops! :-\\")
        #print(erro)
        com1.disable()
        
if __name__ == "__main__":
    filename = sys.argv[1:][1]
    root = Tk()
    root.withdraw()
    dirname = filedialog.askdirectory(title='Selecione um diretório')
    if('/' in dirname):
        dirname = '\\'.join(dirname.split('/'))
    main(dirname, filename)