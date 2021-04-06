def package(type_pckg,total,index,msg,len_msg=0,id_sensor=b'\xff',id_server=b'\x00'):

    header = type_pckg.to_bytes(1,'big') + id_sensor + id_server + total.to_bytes(1,'big') + index.to_bytes(1,'big')

    if (type_pckg == 3):
        if (len(msg) > 0):
            len_msg = len(msg)
        header += len_msg.to_bytes(1,'big')
    else:
        header += index.to_bytes(1,'big')

    header += index.to_bytes(1,'big') + index.to_bytes(1,'big') + b'\xff\xaa'

    if (len(msg) > 0):
        return header + msg + b'\xff\xaa\xff\xaa'

    return header

def readPackage(package):

    type_pckg = package[0]
    total_pckgs = package[3]
    index = package[4]
    len_msg = package[5]

    if (type_pckg == 3 and len(package) > 10):
        msg = package[:-4]
        eop = package[-1:-5:-1]
        if (len(eop) == 4 and eop == b'\xaa\xff\xaa\xff'):
            eop_check = True
        else:
            eop_check = False

        return type_pckg, total_pckgs, index, msg, len_msg, eop_check
    
    else:
        return type_pckg, total_pckgs, index, len_msg