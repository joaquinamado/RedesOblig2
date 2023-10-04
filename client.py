import socket


def client(server_ip, server_port, vlc_port):

    try:
        master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        master.connect((server_ip, server_port))
        paused = False
        connected = False
        fin = False
        while (not fin):
            command = str(input())
            master.send(command.encode('utf-8'))
            data = master.recv(1024)
            print(data.decode('utf-8'))
            print(connected)
            comandoSinN = command.split('\n')[0]
            if (command.find('CONECTAR') and not connected):
                connected = True
                skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                skt.connect(('127.0.0.1', vlc_port))
            else:
                match comandoSinN:
                    case 'INTERRUMPIR':
                        if(connected and not paused):
                            paused = True
                        pass
                    case 'CONTINUAR':
                        if(connected and paused):
                            paused = False
                        pass
                    case 'DESCONECTAR':
                        if(connected):
                            connected = False
                            fin = True
                            master.close()
                            skt.close()
                        pass
                    case _ :
                        if(connected and not paused):
                            datagram = skt.recv(1024)
                        pass
            command = ''
            comandoSinN = ''


    except socket.error as e:
        print(str(e))



client("127.0.0.1", 65535, 65534)
