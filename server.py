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
    try:
        com1 = enlace(serialName)
        com1.enable()
        com1.rx.fisica.flush()
        log = open('server.txt','w')
        
        print('Starting communication...\n')

        init = False
        print('Trying to stablish handshake...')
        while (not init):

            while (com1.rx.getBufferLen() < 10):
                pass
            
            log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                      ' / receb / 1 / 10\n')
            ans, nAns = com1.getData(10)
            type_pckg, total_pckgs, index, len_msg = readPackage(ans)

            if (type_pckg == 1):
                init = True
                numPckgs = total_pckgs
                time.sleep(1)

        head = package(type_pckg=2,total=0,index=0,msg=b'')
        log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                  ' / envio / 2 / 10\n')
        com1.sendData(np.asarray(head))
        while com1.tx.getStatus() != len(head):
            pass

        print('Handshaked!\n')

        rxBuffer = b''
        cont = 1
        print('Receiving pckgs...\n')
        while (cont <= numPckgs):

            timer1 = time.time()
            timer2 = time.time()

            while (com1.rx.getBufferLen() < 10):
                pass

            head, nHead = com1.getData(10)
            type_pckg, total_pckgs, index, len_msg = readPackage(head)
            log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                      f' / receb / {type_pckg} / {len_msg+14} / {index} / {total_pckgs}\n')
        
            if (type_pckg == 3 and index == cont and len_msg > 0):
                print(f'Receiving {index}th pckg')
                while (com1.rx.getBufferLen() < len_msg + 14):
                    if (time.time() - timer2 > 20):
                        print('Client not responding! Go take a coffee and try later!\n')
                        init = False
                        head = package(type_pckg=5,total=0,index=cont,msg=b'')
                        log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                                  ' / envio / 5 / 10\n')
                        com1.sendData(np.asarray(head))

                        while com1.tx.getStatus() != len(head):
                            pass
                        
                        log.close()
                        com1.disable()
                        return

                    elif (time.time() - timer1 > 2):
                        head = package(type_pckg=4,total=0,index=cont,msg=b'')
                        log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                                  ' / envio / 4 / 10\n')
                        com1.sendData(np.asarray(head))

                        while com1.tx.getStatus() != len(head):
                            pass

                        timer1 = time.time()

                pckg, nPckg = com1.getData(len_msg + 14)
                type_pckg, total_pckgs, index, msg, len_msg, eop_check = readPackage(pckg)

                if (eop_check):
                    print('Successfully received!\n')
                    rxBuffer += msg
                    head = package(type_pckg=4,total=0,index=cont,msg=b'')
                    log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                              ' / envio / 4 / 10\n')
                    com1.sendData(np.asarray(head))

                    while com1.tx.getStatus() != len(head):
                        pass

                    cont += 1
                else:
                    print('Something is wrong, trying again...\n')
                    head = package(type_pckg=6,total=0,index=cont,msg=b'')
                    log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                              ' / receb / 6 / 10\n')
                    com1.sendData(np.asarray(head))

                    while com1.tx.getStatus() != len(head):
                        pass
            else:
                head = package(type_pckg=6,total=0,index=cont,msg=b'')
                log.write(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + 
                            ' / receb / 6 / 10\n')
                com1.sendData(np.asarray(head))

                while com1.tx.getStatus() != len(head):
                    pass

        log.close()
        f = open(imgW,'wb')
        f.write(rxBuffer)
        f.close()
        
        com1.disable()
    
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        log.close()
        com1.disable()
        
if __name__ == "__main__":
    filename = sys.argv[1:][1]
    root = Tk()
    root.withdraw()
    dirname = filedialog.askdirectory(title='Selecione um diretório')
    if('/' in dirname):
        dirname = '\\'.join(dirname.split('/'))
    main(dirname, filename)