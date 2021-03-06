#!/usr/bin/python

import pexpect, os, socket, re

def localCmd(_cmd) : 
    _p = os.popen(_cmd)
    _data = _p.read()
    _p.close()
    return _data

def GetIP() :
    return socket.gethostbyname(socket.getfqdn(socket.gethostname()))

def IsPublicIP(addr) :
    _reIP = r"^(2[0-4]\d|25[0-5]|[01]?\d?\d)(\.(2[0-4]\d|25[0-5]|[01]?\d?\d)){3}$"
    if re.match(_reIP, addr) == None :
        print("%s is not a valid IP address"%addr)
        os._exit(0)
    _rePrivIP = r"^(192\.168|172\.([1][6-9]|[2]\d|3[01]))(\.(2[0-4]\d|25[0-5]|[01]?\d?\d)){2}" \
        "|10(\.(2[0-4]\d|25[0-5]|[01]?\d?\d)){3}$"
    if re.match(_rePrivIP, addr) != None :
        return False
    return True

def IsDirect(dst) :
    if IsPublicIP(dst) == True :
        return True
    _s = GetIP().split(".")
    _d = dst.split(".")
    if len(_s) != len(_d) or len(_s) != 4 :
        print("Invalid IP address: src(%s),dst(%s)"%(GetIP(), dst))
        os._exit(0)
    for _i in range(len(_s)-1) :
        if _s[_i] != _d[_i] :
            return False
    return True


expectRet = [
    '.*assword.*',
    'Last login.*',
    '.*verification.*',
    'Permission denied',
    '.*continue.*?',
    pexpect.EOF,
    pexpect.TIMEOUT,
]

class switchLoginExpect :
    #list = {}
    #err = None
    def __init__(self, s, h):
        self.list = {
            #'password'
            0:self.password,
            #'success'
            1:self.success,
            #'verifycode'
            2:self.verification,
            #'permission'
            3:self.denied,
            #'continue'
            4:self.sendYes
        }
        self.ssh = s
        self.host = h
        #function = self.list.get(expt, self.default)
        #function()
    def switch(self, expt) :
        func = self.list.get(expt, self.default)
        return func()
    def Run(self) :
        while True :
            _r = self.switch(self.ssh.expect(expectRet, timeout = 60))
            if _r == 0 :
                continue
            elif _r > 0 :
                return self.ssh
            return None
    def default(self):
        print(self.ssh.after)
        #self.err = self.ssh.after
        return  -1
    def password(self):
        self.ssh.sendline(self.host.passwd)
        _swt = switchLoginExpect(self.ssh, self.host)
        return _swt.switch(self.ssh.expect(expectRet, timeout = 60))
    def sendYes(self):
        #print('function sendYes call')
        self.ssh.sendline('yes\n')
        return 0
    def success(self):
        return 1
    def verification(self):
        _vfcode = input('\r\nPlease enter the verification code sent to your mobile phone:')
        self.ssh.sendline(_vfcode)
        return 0
    def denied(self):
        localCmd('chmod 400 %s'%(os.path.dirname(__file__) + '/key/%s'%(self.host.key)))
        print('key file mod change to 400, try again!')
        #self.err = 'key file mod change to 400, try again!'
        return -1

class Host :
    def __init__(self, _ip, _port, _usrname, _passwd, _key, _alias, _route) :
        self.ip = _ip
        self.port = _port
        self.usrname = _usrname
        self.passwd = _passwd
        self.key = _key
        self.alias = _alias
        self.route = _route
    def getSSHLoginCmd(self) :
        if self.key != '' :
            kpath = os.path.dirname(__file__) + '/key/%s'%(self.key)
            return 'ssh -p %d %s@%s -i %s'%(self.port, self.usrname, self.ip, kpath)
        else :
            return 'ssh -p %d %s@%s'%(self.port, self.usrname, self.ip)
    def SSH(self) :
        if self.route == None :
            _shell = pexpect.spawn(self.getSSHLoginCmd())
            print('Login@%s ......'%self.ip)
            return switchLoginExpect(_shell, self).Run()
        else :
            _route = self.route.SSH()
            if _route == None :
                return None
            _route.sendline(self.getSSHLoginCmd())
            print('Login@%s ......'%self.ip)
            return switchLoginExpect(_route, self).Run()
    def getError(self, e) :
        return "Host(%s) error: %s"%(self.ip, e)
    def Shell(self) :
        _shell = self.SSH()
        if _shell == None :
            return
        _rows, _columns = os.popen('stty size', 'r').read().split()
        _shell.setwinsize(int(_rows), int(_columns))
        print('Welcome to %s\n'%(self.ip))
        _shell.interact()

class Operate :
    def __init__(self, _host) :
        self.host = _host
    def PutFile(self) :
        pass

class Node :
    def __init__(self, _childs, _operate) :
        self.childs = _childs
        self.operate = _operate
    def Add(self, child) :
        self.childs

class Trie :
    def __init__(self) :
        self.nodes = {}

class Task :
    def __init__(self, _hostlist, _operate) :
        self.hostlist = _hostlist
        self.operate = _operate


#try :
#    _idx = int(input('Enter the number:'))
#except :
#    os._exit(0)
#if _idx > len(hs186) :
#    os._exit(0)
#hs186[_idx].Shell()
ipstr = input('Enter the ip:')
if IsDirect(ipstr) == True :
    print(ipstr, 'direct')
else :
    print(ipstr, 'two network')