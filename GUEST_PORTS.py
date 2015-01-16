# import the needed libraries
import paramiko
import time
import os
import re
import sys
# pull in the username and password from a separate file
import cred 

# takes in the IP Address for the device from the command line
addr = sys.argv[1] 

# function defined to turn off terminal length and not require the more command
def disable_paging(command="terminal length 0\n", delay=1):
	remote_conn.send("\n")
	remote_conn.send(command)
	time.sleep(delay)

enablepass=cred.password
# defines enable  and conf t for logging into the router
def enable(command1="en\n", command2="cred.password\n", command3="conf t\n",delay=1):
	remote_conn.send("\n")
	remote_conn.send(command1)
	time.sleep(delay)
	remote_conn.send(command2)
	time.sleep(delay)
	remote_conn.send(command3)
	time.sleep(delay)

# open a file to dump the data in for the sh ip int brief
int_file = open("int_file.txt", "w")

# login for paramiko to get in
remote_conn_pre = paramiko.SSHClient()
remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
remote_conn_pre.connect(addr, username=cred.username, password=cred.password, allow_agent=False,look_for_keys=False)
remote_conn = remote_conn_pre.invoke_shell()

disable_paging()
# send the new line to make sure we have a clean line
#remote_conn.send("\n")

# command to send
remote_conn.send("sh int | i notconnect|Last input never|Last in.*[1-9]w\n")

# make it seem like a user is there to pause output
time.sleep(1)

# pull back the max amount of data possible and put into the data file and then close the file
int_file.write(remote_conn.recv(65525))
int_file.close()
#open the file back up and then use it again as a readonly source for the next part
int_file = open("int_file.txt", "r")
cmd_file = open("cmd_file.txt", "w")

# split the data that was received previously looking for Eth, if so put it into a new file and then format it correctly
for line in int_file:
	columns = line.split(' ')[0]
	if re.search('Eth', columns, re.I):
		cmd_file.write("interface " +  columns + "\n")	
		cmd_file.write(" switchport access vlan 10\n")
	else:
		pass

#Close the files now that I am done going through them
cmd_file.close()
int_file.close()

#run the enable part of the command to get us into the correct mode
enable()

#open the command file and then run the next set of commands
cmd_file = open("cmd_file.txt", "r")
output = open("output.txt", "w")
for line in cmd_file:
	remote_conn.send(line)
	time.sleep(1)
	output.write(remote_conn.recv(65525))

#close the files when done
output.close()
cmd_file.close()
# close the connection
remote_conn_pre.close()
