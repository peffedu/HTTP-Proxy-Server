# HTTP-Proxy-Server
Syntax: python mproxy.py <options> <port number>

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
