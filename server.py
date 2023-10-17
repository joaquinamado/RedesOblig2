import socket
import threading
import sys
from queue import Queue

clientes = {}

def main(server_ip, server_port):
    try:
        socket.inet_aton(server_ip)
        cola = Queue()
        threading.Thread(target=recibirVLC, args=(server_ip, server_port, cola)).start()
        threading.Thread(target=enviadorClientes, args=(server_ip, cola)).start()
        master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        master.bind((server_ip, server_port))
        master.listen(5)
        while True:
            client, address = master.accept()
            threading.Thread(target=controladorCliente, args=(1, client)).start()

        #master.close()
    except socket.error as e:
        print(str(e))


def recibirVLC(server_ip, server_port, cola):
    master_vlc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    master_vlc.bind((server_ip, 65529))
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
    while True:
        data = client.recv(4096)
        if not data:
            client.close()
            break
        buff += data.decode('utf-8')

        while '\n' in buff:
            primer_comando, buff = buff.split('\n', 1)
            print(primer_comando)
            print (client.getpeername()[0])
            print (conectado)
            print (pausado)

            if (primer_comando.startswith("CONECTAR ")):
                # Por si no agrega el puerto al comando 
                try:
                    puerto = int(primer_comando.replace("CONECTAR ", ""))
                except ValueError:
                    client.send("OK\n".encode('utf-8'))
                    continue
                clientes[(client.getpeername()[0], puerto)] = True
                conectado = True
                client.send("OK\n".encode('utf-8'))
            elif primer_comando.startswith("INTERRUMPIR"):
                if conectado and not pausado:
                    pausado = True
                    clientes[(client.getpeername()[0], puerto)] = False
                    client.send("OK\n".encode('utf-8'))
            elif primer_comando.startswith("CONTINUAR"):
                if conectado and pausado:
                    pausado = False
                    clientes[(client.getpeername()[0], puerto)] = True
                    client.send("OK\n".encode('utf-8'))
            elif primer_comando.startswith("DESCONECTAR"):
                if conectado:
                    #del clientes[(client.getpeername()[0], puerto)]
                    clientes.pop((client.getpeername()[0], puerto))
                client.send("OK\n".encode('utf-8'))
                client.close()
                return 
            else:
                continue

def enviadorClientes (server_ip, cola):
    enviador = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    enviador.bind((server_ip, 65533))
    while True:
        datagrama = cola.get(block = True)
        for cliente in clientes:
            if (clientes[cliente]):
                enviador.sendto(datagrama, cliente)

#main("127.0.0.1", 65535)
main(str(sys.argv[1]), int(sys.argv[2]))
