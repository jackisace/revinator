#!/usr/bin/env python

import argparse
import socket
import threading
import os
import pdb
import time
from spawner import spawner

class connection:
    all = []
    def __init__(self, conn):
        self.conn = conn[0]
        self.addr = conn[1][0]
        self.port = conn[1][1]
        self.sock = socket.socket()
        self.connected = False
        self.revs = []
        self.working_rev = ""
        self.echo_count = None
        self.conn.settimeout(0.2)
        self.kill_cmd = False
        self.parent = None
        self.set_parent()
        self.parent.test_all()
        if not self.echo_cmd_test():
            self.kill()
            self.parent.report_fail()
        else:
            self.parent.report_pass()
            connection.all.append(self)

    def set_parent(self):
        self.parent = spawner.all[self.addr]
        spawner.all[self.addr].children.append(self)


    def kill(self):
        self.conn.close()
        self.sock.close()
        self.kill_cmd = True

    def rcv(self):
        data = ""
        while True:
            try:
                d = self.conn.recv(1024).decode()
                if d:
                   data += d
                else:
                    return data
            except TimeoutError:
                return data
            
    def echo_cmd_test(self):
        self.conn.settimeout(0.2)
        self.rcv()
        cmd = "echo HI_REVINATOR\r\n\r\n"
        self.conn.send(cmd.encode())
        data = self.rcv()
        self.echo_count = data.count("echo HI_REVINATOR")
        if "HI_REVINATOR" not in data.replace("echo HI_REVINATOR", ""):
            return False
        return True

    def connect(self, sock):
        if self.kill_cmd:
            return

        self.sock = sock[0]
        self.conn.setblocking(True)
        #self.conn.settimeout(None)
        threading.Thread(target=self.in_stream).start()
        threading.Thread(target=self.out_stream).start()
        self.connected = True



    def in_stream(self):
        while True:
            if self.kill_cmd:
                return

            try:
                data = self.conn.recv(1024)
            except:
                continue

            if data and len(data) > 0:
                self.sock.sendall(data)
            else:
                time.sleep(0.1)


    def out_stream(self):
        while True:
            if self.kill_cmd:
                return

            try:
                data = self.sock.recv(1024)
            except:
                continue

            if data and len(data) > 0:
                self.conn.sendall(data)
            else:
                time.sleep(0.1)
    

