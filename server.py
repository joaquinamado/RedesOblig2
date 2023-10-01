import socket
import threading


def server():

    try:
        master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        master.bind((socket.gethostname(), 5000))
        master.listen(5)
        while True:
            client, address = master.accept()
            queue = []
            threading.Thread(target=controladorCliente, args=(client, queue))
            threading.Thread(target=enviadorCliente, args=(address, queue))
        
        #master.close()
    except socket.error as e:
        print(str(e))

        

def controladorCliente(client, queue):
    while True:
        buff = ''
        while (not buff.find('\n')):
            data = client.recv(1024)
            buff += data.decode('utf-8')


def enviadorCliente(address, queue):
    conectado = False
    pausado = False
    puerto = -1
    ultEnviado = -1
    try:
        while True:
            if (not conectado):
                mensaje = queue.pop(0)
                if (mensaje.isnumeric()):
                    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    skt.bind(('192.168.0.125', ))
                    puerto = int(mensaje)
                elif (mensaje == 'desconectar'):
                    return
            else:
                if (not queue.empty()):
                    mensaje = queue.pop(0)
                    match mensaje:
                        case 'continuar':
                            pausado = False
                        case 'pausa':
                            pausado = True 
                        case 'desconectar':
                            skt.close()
                            return
                        case _:
                            pass
    except socket.error as e:
        print(str(e))
        return




