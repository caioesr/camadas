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
import sys

serialName = "COM3"

def main(filename):
    imgR = filename
    try:
        com1 = enlace(serialName)
        com1.enable()
        com1.rx.fisica.flush()
        print('Comunication with port created!\n')

        txBuffer = open(imgR,'rb').read()
        msgs = [txBuffer[i:i+114] for i in range(0,len(txBuffer),114)]
        numPckgs = len(msgs)
        log = open('client.txt','w')

        init = False
        print('Trying to stablish handshake server...')
        while (not init):

            head = package(type_pckg=1,total=numPckgs,index=0,msg=b'')
            log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                      ' / envio / 1 / 10\n')
            com1.sendData(np.asarray(head))
            while com1.tx.getStatus() != len(head):
                pass

            start = time.time()
            while (com1.rx.getBufferLen() < len(head)):
                if (time.time() - start >= 5):
                    break
            
            if (com1.rx.getBufferLen() == len(head)):
                log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                      ' / receb / 2 / 10\n')
                ans, nAns = com1.getData(len(head))
                if (ans[0] == 2):
                    init = True
            else:
                print('Something is wrong, trying again...')

        print('Handshaked!\n')

        cont = 1
        lastIndex = 0
        print('Starting file sending...\n')
        while (cont <= numPckgs):
            
            print(f'Sending {cont}th pckg...')
            head = package(type_pckg=3,total=numPckgs,index=cont,msg=b'',len_msg=len(msgs[cont-1]))
            log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                      f' / envio / 3 / {len(msgs[cont-1])+14} / {cont} / {numPckgs}\n')
            com1.sendData(np.asarray(head))
            while com1.tx.getStatus() != len(head):
                pass

            pckg = package(type_pckg=3,total=numPckgs,index=cont,msg=msgs[cont-1])
            com1.sendData(np.asarray(pckg))
            while com1.tx.getStatus() != len(pckg):
                pass

            timer1 = time.time()
            timer2 = time.time()

            while (com1.rx.getBufferLen() < 10):

                if (time.time() - timer1 >= 5):
                    print('\nServer is taking to long, resending pckg...')
                    log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                              f' / envio / 3 / {len(len(msgs[cont-1])+14)} / {cont} / {numPckgs}\n')
                    com1.sendData(np.asarray(pckg))

                    while com1.tx.getStatus() != len(pckg):
                        pass
                    timer1 = time.time()

                elif (time.time() - timer2 >= 20):
                    head = package(type_pckg=5,total=numPckgs,index=cont,msg=b'')
                    log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                              ' / envio / 5 / 10\n')
                    com1.sendData(np.asarray(head))

                    while com1.tx.getStatus() != len(head):
                        pass
                    print('\nTimed out! Go take a coffee and try again later!\n')
                    log.close()
                    com1.disable()
                    return

            if (com1.rx.getBufferLen() == 10):
                ans, nAns = com1.getData(10)
                if (ans[0] == 4):
                    log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                              ' / receb / 4 / 10\n')
                    lastIndex = cont
                    cont += 1
                elif (ans[0] == 6):
                    log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                              ' / receb / 6 / 10\n')
                    print('Something is wrong, trying again...')
                    cont = lastIndex
            else:
                print('Something is wrong, trying again...')

        print('\nTransmission conclude!')
        log.close()
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        log.close()
        com1.disable()
        

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    dirname = filedialog.askopenfile(title='Selecione um arquivo',mode='r')
    filename = dirname.name
    main(filename)
    print('\nCommunication closed!')