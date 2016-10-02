#!/usr/bin/env python
#ds: see virtualception.wordpress.com
#download a file from a guest on a esxi host
#original file was for uploading from the pyvmomi examples (made small changes)
#tested with esxi 6
#added a small workaround for url when downloading file, see below
#added args for running as standalone
#old comment:
"""
Written by Reubenur Rahman
Github: https://github.com/rreubenur/

This code is released under the terms of the Apache 2
http://www.apache.org/licenses/LICENSE-2.0.html

"""


from __future__ import with_statement
import atexit
import shutil
import requests
from tools import cli
from tools import tasks
from pyVim import connect
from pyVmomi import vim, vmodl


def get_args():
    """Get command line args from the user.
    """

    parser = cli.build_arg_parser()

    parser.add_argument('-v', '--vm_uuid',
                        required=False,
                        action='store',
                        help='Virtual machine uuid')

    parser.add_argument('-r', '--vm_user',
                        required=False,
                        action='store',
                        help='virtual machine user name')

    parser.add_argument('-w', '--vm_pwd',
                        required=False,
                        action='store',
                        help='virtual machine password')

    parser.add_argument('-l', '--path_inside_vm',
                        required=False,
                        action='store',
                        help='Path inside VM for upload')

    parser.add_argument('-f', '--download_file',
                        required=False,
                        action='store',
                        help='Path of the file to be downloaded from guest. If missing file is printed to screen')

    args = parser.parse_args()

    cli.prompt_for_password(args)
    return args


def main():
    """
    Simple command-line program for downloading a file from guest
    """

    args = get_args()
    vm_path = args.path_inside_vm
    try:
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port))

        atexit.register(connect.Disconnect, service_instance)
        content = service_instance.RetrieveContent()
        vm = service_instance.content.searchIndex.FindByUuid(None, args.vm_uuid, True, True)
        #print ("hello:"+str(vm))
        horst=args.host
        
        tools_status = vm.guest.toolsStatus
        if (tools_status == 'toolsNotInstalled' or
                tools_status == 'toolsNotRunning'):
            raise SystemExit(
                "VMwareTools is either not running or not installed. "
                "Rerun the script after verifying that VMWareTools "
                "is running")

        creds = vim.vm.guest.NamePasswordAuthentication(
            username=args.vm_user, password=args.vm_pwd)

        try:
            file_attribute = vim.vm.guest.FileManager.FileAttributes()
            #url = content.guestOperationsManager.fileManager. \
            #    InitiateFileTransferToGuest(vm, creds, vm_path,
            #                                file_attribute,
            #                                len(args), True)
            url = content.guestOperationsManager.fileManager. \
                InitiateFileTransferFromGuest(vm, creds, vm_path)
            #print ("url: "+url.url)	
            
            #ds: workaround for wrong url if using esxi
            url2=url.url.replace ('*', horst)
           
            resp = requests.get(url2, verify=False)
            if not resp.status_code == 200:
                print "Error while downloading file"
            else:
                print "Successfully downloaded file"
                if args.download_file:                
                    f = open(args.download_file, 'wb')
                    f.write(resp.content)
                    f.close()
                else:
                    print ("Output: " + resp.text)
        except IOError, e:
            print e
    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()
