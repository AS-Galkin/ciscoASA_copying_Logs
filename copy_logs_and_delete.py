#!/usr/bin/python

import subprocess
import getpass
import sys
import telnetlib
import time, datetime
import paramiko

ips = ['IP_ADDRESS', 'IP_ADDRESS']

def create_connection(HOST):
        print(" Try connect to"+": "+HOST)
        try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(HOST, username='YOUR_USERNAME', password='YOUR_PASSWORD')
                ssh = client.invoke_shell()
                ssh.send("en\n")
                time.sleep(1)
                ssh.send('YOUR_PASSWORD\n')
                time.sleep(1)
                create_list_of_logs(ssh, HOST)
        except:
                print('Cannot create connection ' + HOST)
                pass

def create_list_of_logs(ssh, HOST):
        try:
                ssh.send('dir flash:/syslog/' + '\n')
                time.sleep(2)

                #create list of logs
                result = ssh.recv(4096).decode('ascii').split('\n')
                while result[len(result)-1] == '<--- More --->':
                        ssh.send(' ')
                        time.sleep(1)
                        tmp_stdout = ssh.recv(4096).decode('ascii').split('\n')
                        tmp_stdout.pop(0)
                        for i in tmp_stdout:
                                result.append(i)
                        if tmp_stdout[len(tmp_stdout)-1] == 'ASA5520-C1U-SPUN#':
                                break

                while True:
                        try:
                                result.remove('<--- More --->')
                        except:
                                break

                for index in range (7,len(result)-4):
                        tmp_str = result[index].split(' ')
                        for i in range(len(tmp_str)):
                                if i == 15:
                                        result[index] = tmp_str[i]

                # for i in range(len(result)):
                #         print(i, result[i])

                copy_logs(ssh, result, HOST)
        except:
                print('Cannot create list of logs ' + HOST)
                pass

def copy_logs(ssh, result, HOST):
        try:
                ssh.send('cd disk0:/syslog/\n')
                time.sleep(1)
                for index in range (7,len(result)-4):
                        print('Copying ' + result[index])
                        ssh.send('copy disk0: disk1:\n')
                        time.sleep(1)
                        ssh.send(result[index] + '\n')
                        time.sleep(1)
                        ssh.send(result[index] + '\n')
                        time.sleep(1)
                        tmp_stdout = ssh.recv(4096).decode('ascii').split('\n')
                        #print(tmp_stdout)
                        if 'Do you want to over write? [confirm]' in tmp_stdout:
                                print('Overwriting process..')
                                ssh.send('\n')
                        time.sleep(15)
                del_logs(ssh, result, HOST)
        except:
                print('Cannot copy logs ' + HOST + "!")
                pass

def del_logs(ssh, result, HOST):
        try:
                ssh.send('delete disk0:/syslog/LOG-*\n')
                time.sleep(1)
                for _ in range(len(result)):
                        ssh.send('\n')
                        ssh.sleep(1)
                ssh.send('exit\n')
                ssh.close()
        except:
                print('Cannot delete logs ' + HOST)
                pass

for i in ips:
        connection = create_connection(i)