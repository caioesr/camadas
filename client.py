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
from utils import *

serialName = "COM3"

def main(filename):
    imgR = filename
    try:
        com1 = enlace(serialName)
        com1.enable()
        print('Comunication with port created!\n')

        txBuffer = open(imgR,'rb').read()
        msgs = [txBuffer[i:i+128] for i in range(0,len(txBuffer),128)]
        number_of_pckgs = len(msgs)
        msg = number_of_pckgs.to_bytes(1,'big')
        pckg = package(index=0,msg=msg,next=msgs[0])
        print(f'Sending size of full content ({number_of_pckgs} packages)')
        com1.sendData(np.asarray(pckg))
        while com1.tx.getStatus() != len(pckg):
            pass
        print('Sucess!\n')

        print('Waiting for server response...')
        ans, nAns = com1.getData(15)
        msg = readPackage(ans)[1]
        if(msg == b'\xff'):
            print('Starting file transference\n')
        else:
            print('Something goes wrong, wait one minute and try again\n')
            return

        index = 1
        count = 0
        while count < number_of_pckgs:
            index = count+1
            msg = msgs[count]
            if(count < number_of_pckgs-1):
                pckg = package(index=index,msg=msg,next=msgs[count+1])
            else:
                pckg = package(index=index,msg=msg,next=None)

            print(f'Sending {index}th package...')
            com1.sendData(np.asarray(pckg))
            while com1.tx.getStatus() != len(pckg):
                pass
            
            ans, nAns = com1.getData(15)
            msg = readPackage(ans)[1]
            if(msg == b'\xff'):
                count += 1
            else:
                print('Something goes wrong, trying again...')

        print('\nTransmission conclude!')
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    dirname = filedialog.askopenfile(title='Selecione um arquivo',mode='r')
    filename = dirname.name
    main(filename)