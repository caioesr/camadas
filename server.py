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
from utils import *

serialName = "COM4"

def main(dirname, filename):
    imgW = f'{dirname}\{filename}'
    #try:
    com1 = enlace(serialName)
    com1.enable()
    
    print('Starting communication...')

    initPackage, nInitPackage = com1.getData(15)
    index, msg, size_next, eop_check = readPackage(initPackage)
    
    if eop_check and (index == 0):
        print('Communication stablished!\n')
        pckg = package(index=0,msg=b'\xff',next=None)
    else:
        print('Something goes wrong, wait one minute and try again\n')
        pckg = package(index=0,msg=b'\x00',next=None)
        return

    com1.sendData(np.asarray(pckg))
    while com1.tx.getStatus() != len(pckg):
        pass

    rxBuffer = b''
    count_pckgs = 0
    while count_pckgs < int.from_bytes(msg, 'big'):

        print(f'Receiving {count_pckgs+1}th package...')
        pckg, nPckg = com1.getData(size_next+14)
        new_index, new_msg, new_size_next, eop_check = readPackage(pckg)

        if(new_index == index + 1) and eop_check:
            pckg = package(index=0,msg=b'\xff',next=None)
            rxBuffer += new_msg
            index = new_index
            size_next = new_size_next
            count_pckgs += 1
        else:
            print('Error! Retrying...')
            pckg = package(index=0,msg=b'\x00',next=None)

        com1.sendData(np.asarray(pckg))
        while com1.tx.getStatus() != len(pckg):
            pass
    
    f = open(imgW,'wb')
    f.write(rxBuffer)
    f.close()

    # Encerra comunicação
    print('\nTransmission conclude!')
    
    com1.disable()
    
    # except Exception as erro:
    #     print("ops! :-\\")
    #     print(erro)
    #     com1.disable()
        
if __name__ == "__main__":
    filename = sys.argv[1:][1]
    root = Tk()
    root.withdraw()
    dirname = filedialog.askdirectory(title='Selecione um diretório')
    if('/' in dirname):
        dirname = '\\'.join(dirname.split('/'))
    main(dirname, filename)