# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 18:26:30 2021

@author: caioe
"""

from enlace import *
import time
import numpy as np
from tkinter import filedialog, Tk
import time

serialName = "COM3"
header_size = 3

def main(filename):
    try:
        com1 = enlace(serialName)
        com1.enable()
        print('Comunicação aberta com sucesso!')
                
        imgR = filename
        txBuffer = open(imgR,'rb').read()
        header = len(txBuffer).to_bytes(header_size,'big')
        msg = header + txBuffer
          
        f = open('history.txt','w')
        f.write(str(time.time()))
        f.close()
        
        com1.sendData(np.asarray(header))
        
        while com1.tx.getStatus() != header_size:
            pass
        print('Header recebido!')
        
        com1.sendData(np.asarray(txBuffer))
        print('Transmissao concluida!')
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    dirname = filedialog.askopenfile(title='Selecione um diretório',mode='r')
    filename = dirname.name
    main(filename)