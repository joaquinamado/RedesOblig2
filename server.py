import socket
import threading
import os
from queue import Queue

fin = False
clientes = {}

def main(server_ip, server_port):
    try:
        cola = Queue()
        threading.Thread(target=recibirVLC, args=(server_ip, server_port, cola)).start()
        threading.Thread(target=enviadorClientes, args=(1, cola)).start()
        master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        master.bind((server_ip, server_port))
        master.listen(5)
        while True:
            print('Esperando conexion')
            client, address = master.accept()
            print('Llego conexion')
            threading.Thread(target=controladorCliente, args=(1, client)).start()

        #master.close()
    except socket.error as e:
        print(str(e))


def recibirVLC(server_ip, server_port, cola):
    master_vlc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    master_vlc.bind((server_ip, server_port))
    #os.system('cvlc -vvv videoPrueba.mp4 --sout "#transcode{vcodec=mp4v,acodec=mpga} rtp{proto=udp, mux=ts, dst=127.0.0.1, port=65534}" --loop --ttl 1')
    while True:
        data = master_vlc.recv(4096)
        if data:
            cola.put(data)
        else:
            break
    master_vlc.close()


def controladorCliente(num, client):
    pausado = False
    conectado = False
    buff = ""
    recibidoComando = False
    while True:
        while not recibidoComando:
            print('Esperando comando')
            data = client.recv(4096)
            if(not data):
                client.close()
                break
            buff += data.decode('utf-8')
            print(buff)
            recibidoComando = buff.find('\n') != -1

        primer_comando = buff.split('\n')[0]
        indice = buff.find('\n') + 1
        buff = buff[indice:]

        puerto = client.getpeername()[1]
        if(primer_comando.find("CONECTAR") != -1):
            try:
                puerto = int(primer_comando.replace("CONECTAR ", ""))
            except ValueError:
                puerto = client.getpeername()[1]
            clientes[(client.getpeername()[0], puerto)] = True
            conectado = True
            client.send("OK\n".encode('utf-8'))
        else:
            match primer_comando:
                case "INTERRUMPIR":
                    if conectado and not pausado:
                        pausado = True
                        clientes[(client.getpeername()[0], puerto)] = False
                        client.send("OK\n".encode('utf-8'))
                case "CONTINUAR":
                    if conectado and pausado:
                        pausado = False
                        clientes[(client.getpeername()[0], puerto)] = True
                        client.send("OK\n".encode('utf-8'))
                case "DESCONECTAR":
                    if conectado:
                        clientes.pop((client.getpeername()[0], puerto))
                    client.send("OK\n".encode('utf-8'))
                    client.close()
                    return
                case _:
                    continue

def enviadorClientes (num, cola):
    enviador = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    enviador.bind(('127.0.0.1', 65533))
    while True:
        datagrama = cola.get(block = True)
        for cliente in clientes:
            if (clientes[cliente]):
                enviador.send(cliente, datagrama)

main("127.0.0.1", 65535)
