def package(index,msg,next,eop=b'\xff',eop_size=4):

    if(next is None):
        header = index.to_bytes(6,'big') + len(msg).to_bytes(1,'big') + eop + eop_size.to_bytes(1,'big') + b'\x00'
    else:
        header = index.to_bytes(6,'big') + len(msg).to_bytes(1,'big') + eop + eop_size.to_bytes(1,'big') + len(next).to_bytes(1,'big')
    
    pckg = header + msg + eop*eop_size

    return pckg

def readPackage(package):

    header = package[:10]
    index = int.from_bytes(header[:6], 'big')
    try:
        size_msg = int.from_bytes(header[6], 'big')
    except:
        size_msg = header[6]
    eop_byte = header[7]
    eop_size = header[8]
    size_next_msg = header[9]

    eop = package[10+size_msg:]
    msg = package[10:10+size_msg]
    
    if(len(eop) == eop_size and eop == eop_byte.to_bytes(1,'big')*eop_size):
        eop_check = True
    else:
        eop_check = False

    return index, msg, size_next_msg, eop_check