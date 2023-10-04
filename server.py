import socket
import threading
import os
from queue import Queue 

datagramas = []
ultDatagrama = 0
fin = False

def main(server_ip, server_port):
    try:
        threading.Thread(target=recibirVLC, args=(server_ip, server_port))
        master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        master.bind((server_ip, server_port))
        master.listen(5)
        while True:
            print('Esperando conexion')
            client, address = master.accept()
            print('Llego conexion')
            queue = Queue()
            threading.Thread(target=controladorCliente, args=(client, queue)).start()
            threading.Thread(target=enviadorCliente, args=(address, queue)).start()
        
        #master.close()
    except socket.error as e:
        print(str(e))

        
def recibirVLC():
    master_vlc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    master_vlc.bind(('127.0.0.1', 65534))
    os.system('cvlc -vvv videoPrueba.mp4 --sout "#transcode{vcodec=mp4v,acodec=mpga} rtp{proto=udp, mux=ts, dst=127.0.0.1, port=65534}" --loop --ttl 1')
    while True:
        data, address = master_vlc.recv(1024)
        if (data != '' ):
            datagramas.append(data)
        else:
            break
    master_vlc.close()


def controladorCliente(client, queue):
    while True:
        print('Esperando comando')
        buff = ''
        recibidoComando = False
        data = client.recv(1024)
        buff += data.decode('utf-8')
        print(buff)
        if(not data):
            queue.put('desconectar')
            client.close()
            continue
        else:
            recibidoComando = True

        #while (not recibidoComando):
        #    data = client.recv(1024)
        #    buff += data.decode('utf-8') 
        #    print(buff)
        #    if(not data):
        #        queue.put('desconectar')
        #        client.close()
        #        continue 
        #    else:
        #        recibidoComando = True
        primer_comando = buff.split('\n')[0]
        buff = ''

        if(primer_comando.find("CONECTAR")):
            queue.put(primer_comando.replace("CONECTAR ", ""))
            client.send("OK\n".encode('utf-8'))
        else:
            match primer_comando:
                case "INTERRUMPIR":
                    queue.put("pausa")
                    client.send("OK\n".encode('utf-8'))
                case "CONTINUAR":
                    queue.put("continuar")
                    client.send("OK\n".encode('utf-8'))
                case "DESCONECTAR":
                    queue.put("desconectar")
                    client.send("OK\n".encode('utf-8'))
                    client.close()
                    return
                case _:
                    continue

def enviadorCliente(address, queue):
    conectado = False
    print('Esperando puerto')
    pausado = False
    puerto = -1
    ultEnviado = -1
    try:
        while True:
            if (not conectado):
                mensaje = queue.get()
                if (mensaje.isnumeric()):
                    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    skt.bind(('192.168.0.125', ''))
                    puerto = int(mensaje)
                    skt.connect((address, puerto))
                    print('LLEGO')
                    conectado = True
                elif (mensaje == 'desconectar'):
                    return
            else:
                if (not queue.empty()):
                    mensaje = queue.get()
                    match mensaje:
                        case 'continuar':
                            pausado = False
                        case 'pausa':
                            if(not pausado):
                                pausado = True 
                        case 'desconectar':
                            if(conectado):
                                skt.close()
                            return
                        case _:
                            pass
                elif (not pausado and conectado):
                    if (ultDatagrama > ultEnviado):
                        skt.send(datagramas[++ultEnviado])
    except socket.error as e:
        print(str(e))
        return

main("127.0.0.1", 65535)


