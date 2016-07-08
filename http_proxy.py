#!/usr/bin/env python
import os,sys,getopt,thread,socket, textwrap

#Constant Variables
BACKLOG = 50            # how many pending connections queue will hold
BUFF = 4096    # max number of bytes we receive at once

def print_help():
    print textwrap.dedent("""\
        Syntax: python http_proxy.py <options> <port number>

        HTTP Proxy Server
        Options:
         -h, --help                         
         Prints a synopsis of the application usage and exits with return code 0.

         -v, --version                      
         Prints the name of the app., the version number, the author and exits, returning 0.

         -p, --port <port>                  
         The port your server will be listening on. If the port you try is already occupied, just try another.

         -n, --numworker <num_of_worker>    
         This parameter specifies the number of workers in the thread pool used for handling concurrent HTTP requests. (default: 10)

         -t, --timeout <timeout>            
         The time (seconds) to wait before give up waiting for response from server. (default: infinite)

         -l, --log <logfile>                
         Logs all the HTTP requests and their corresponding responses under the directory specified by log.
        """)\


class OptionInfo:
    def __init__(self):
        # Configuration options, set to default values
        self.port = 8000
        self.host = ''
        self.numworker = 10
        self.timeout = -1
        self.logfile = None
        self.logbool = False
        self.logindex = -1

def parse_options():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvp:n:t:l:")
    except getopt.GetoptError, e:
        print str(e)
        print_help()
        exit(0)

    opts = dict([(k.lstrip('-'), v) for (k,v) in opts])

    if 'h' in opts:
        print_help()
        exit(0)

    if 'v' in opts:
        print """\

    HTTP Proxy Server v0.1
    Ryan Peffers
    """
        exit(0)

    initProx = OptionInfo()

    if 'p' in opts:
        initProx.port = int(opts['p'])
        if (initProx.port > 0 and initProx.port < 65535):
            pass
        else:
            print_help()
            exit(0)
    else:
        print_help()
        exit(0)

    if 'n' in opts:
        initProx.numworker = int(opts['n'])

    if 't' in opts:
        initProx.timeout = int(opts['t'])

    if 'l' in opts:
        initProx.logbool = True
        initProx.logfile = opts['l']
        curr_directory = os.path.dirname(os.path.abspath(__file__))  # get current working directory
        if (initProx.logfile == ("" or ".")):
            initProx.logfile = curr_directory
            pass
        elif (initProx.logfile == None):
            print_help()
            exit(0)
        else:
            initProx.logfile = os.path.join(curr_directory, initProx.logfile)
            try:
                os.makedirs(initProx.logfile)
            except OSError:
                pass

    return initProx

def make_log_name(logindex, ip, url):
    global proxyRun
    filename = str(logindex) + "_" + str(ip) + "_" + url
    path = os.path.join(proxyRun.logfile, filename)
    return path


def make_thread(conn, client_address):
    global proxyRun
    proxyRun.logindex += 1
    # get the request from browser
    request = conn.recv(BUFF)
    # print "client_address: ", client_address
    # print "conn: ", conn
    ip = client_address[0]
    # parse the first line get
    first_line = request.split('n')[0]
    # print "first line: ", first_line
    request_type = first_line.split(' ')[0]
    if (request_type == "CONNECT"):
        conn.close()
        print "Cannot handle HTTPS request"
        exit(1)

    url = first_line.split(' ')[1]
    # print "URL: ", url

    # parse webserver and port
    http_position = url.find("://")          # find position of :// to parse around it
    # print "HTTP position: ", http_position
    if (http_position== -1):
        temp = url
    else:
        temp = url[(http_position+3):]       # grab the rest of url
        # print "Rest of URL: ", temp

    port_pos = temp.find(":")

    webserver_position = temp.find("/")
    # print "webserver position: ", webserver_position
    if webserver_position == -1:
        webserver_position = len(temp)
        # print "webserver position new: ", webserver_position


    webserver = ""
    request_port = -1
    if (port_pos==-1 or webserver_position < port_pos):      # default port
        request_port = 80
        webserver = temp[:webserver_position]
    else:       # specific port
        request_port = int((temp[(port_pos+1):])[:webserver_position-port_pos-1])
        webserver = temp[:port_pos]

    # print "Connect to:", webserver, request_port
    if(proxyRun.logbool == True):
        name = make_log_name(proxyRun.logindex, ip, webserver)
        open_file = open(name, "w")
        open_file.write(request)
        open_file.write("\n\n")
    try:
        # connect to the webserver
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, request_port))
        s.send(request)         

        while 1:
            # receive data from webserver
            data = s.recv(BUFF)
            # print "data: ", data

            if (len(data) > 0):
                # send to browser and to log
                if(proxyRun.logbool == True):
                    open_file.write(data)
                conn.send(data)
            else:
                break
        s.close()
        conn.close()

    except socket.error, (value, message):
        if s:
            s.close()
        if conn:
            conn.close()
        sys.exit(1)


def main():
    global proxyRun
    proxyRun = parse_options()

    try:
        # create a socket
        newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # associate the socket to host and port
        newSocket.bind((proxyRun.host, proxyRun.port))
        # listening
        newSocket.listen(BACKLOG)

    except socket.error, (value, message):
        if newSocket:
            newSocket.close()
        print "Error opening socket:", message
        sys.exit(1)

    print "Proxy server listening on port: ", proxyRun.port
    # get the connection from client
    while 1:
        conn, client_address = newSocket.accept()
        # create a thread to handle request
        thread.start_new_thread(make_thread, (conn, client_address))

    newSocket.close()

if __name__ == '__main__':
    main()


