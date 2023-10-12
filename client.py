import socket


def client(server_ip, server_port, vlc_port):

    try:
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

            if (command.find('CONECTAR') != -1 and not connected):
                connected = True
            else:
                match command:
                    case 'INTERRUMPIR\n':
                        if(connected and not paused):
                            paused = True
                        pass
                    case 'CONTINUAR\n':
                        if(connected and paused):
                            paused = False
                        pass
                    case 'DESCONECTAR\n':
                        if(connected):
                            connected = False
                            break
                        pass
                    case _ :
                        continue

            master.sendall(command.encode('utf-8'))
            data = master.recv(4096)
            if "OK" not in data.decode('utf-8'):
                break

            print(data.decode('utf-8'))

        master.close()


    except socket.error as e:
        print(str(e))



client("127.0.0.1", 65535, 65534)
