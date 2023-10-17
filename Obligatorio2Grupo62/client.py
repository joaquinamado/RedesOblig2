import socket
import sys

def client(server_ip, server_port, vlc_port):

    try:
        socket.inet_aton(server_ip)
        master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        master.connect((server_ip, server_port))
        paused = False
        connected = False
        while True:
            command = str(input())
            if command == 'CONECTAR':
                command += ' ' + str(vlc_port) + '\n'
            else:
                command += '\n'

            if (command.startswith('CONECTAR') != -1 and not connected and command.find('DES') == -1):
                connected = True
            else:
                match command:
                    case 'INTERRUMPIR\n':
                        if(connected and not paused):
                            paused = True
                    case 'CONTINUAR\n':
                        if(connected and paused):
                            paused = False
                    case 'DESCONECTAR\n':
                        if(connected):
                            connected = False
                    case _ :
                        continue

            master.sendall(command.encode('utf-8'))
            data = master.recv(4096)
            if "OK" not in data.decode('utf-8') or not connected:
                break

            print(data.decode('utf-8'))

        master.close()

    except socket.error as e:
        print(str(e))



#client("127.0.0.1", 65535, 65534)
client(str(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
