import paramiko

import logging.config
log = logging.getLogger(__name__)

logging.getLogger("paramiko").setLevel(logging.WARNING)

class Bridge:
    """
    Bridge between a server and the host. This class uses SSH to connect to external servers.
    """

    username = None
    password = None
    address = None
    local = False

    _ssh = None
    
    def __init__(self, address, username, password, local):
        """
        Initialize the class
        """

        self.address = address
        self.username = username
        self.password = password
        self._ssh = None
        self.local = local

    def disconnect(self):
        """
        Disconnect SSH session
        """
        if self.local == False:
            if self._ssh != None:
                self._ssh.close()

    def connect(self):
        """
        Connect to session
        """
        if self.local == False:
            self.connection()

    def connection(self):
        """
        Create a connection, set ssh paramiko to self signed keys
        """
        if self.local == False:
            if not self.is_connected():
                self._ssh = paramiko.SSHClient()
                self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                self._ssh.connect(self.address, username=self.username, password=self.password)
            return self._ssh
        return None

    def is_connected(self):
        """
        Check if ssh is connected
        """
        if self.local == False:
            transport = self._ssh.get_transport() if self._ssh else None
            return transport and transport.is_active()
        return True

    def sudo_command(self, cmd, pwd):
        """
        Run a command
        """
        result = []
        if self.local == False:
            try:
                transport = self.connection().get_transport()
                session = transport.open_session()
                session.set_combine_stderr(True)
                session.get_pty()
                #for testing purposes we want to force sudo to always to ask for password. because of that we use "-k" key
                session.exec_command("sudo -k " + cmd)
                stdin = session.makefile('wb', -1)
                stdout = session.makefile('rb', -1)
                #you have to check if you really need to send password here 
                stdin.write(pwd +'\n')
                stdin.flush()

                for line in stdout.read().splitlines():        
                    result.append(line)
                return result
            except Exception as e:
                print(e)

    def command(self, cmd):
        """
        Run a command
        """
        result = []
        if self.local == False:
            try:
                ssh_stdin, ssh_stdout, ssh_stderr = self.connection().exec_command(cmd)
                exit_status = ssh_stdout.channel.recv_exit_status()  # Blocking call

                lines = ssh_stdout.read().splitlines()
                for line in lines:
                    result.append(line)

                return result
            except Exception as e:
                print(e)

    def command_single(self, cmd):
        """
        Run a command with a single output
        """
        if self.local == False:
            try:
                ssh_stdin, ssh_stdout, ssh_stderr = self.connection().exec_command(cmd)
                exit_status = ssh_stdout.channel.recv_exit_status()  # Blocking call

                lst = ssh_stdout.read().splitlines()

                result = self._internal_parse_params(lst)

                return result

            except Exception as e:
                print(e)

    def command_array(self, cmd):
        """
        Run a command with multiple output
        """
        if self.local == False:
            try:
                (ssh_stdin, ssh_stdout, ssh_stderr) = self.connection().exec_command(cmd)
                exit_status = ssh_stdout.channel.recv_exit_status()  # Blocking call

                lst = ssh_stdout.read().splitlines()

                result = []
                lsts = [[]]
                lastline = None

                index = 0
                for line in lst:
                    lsts[index].append(line)

                    if line == '' and lastline == '':
                        index = index + 1
                        lsts.append([])

                    lastline = line


                for l in lsts:
                    if len(l) > 0:
                        result.append(self._internal_parse_params(l))

                return result

            except Exception as e:
                print(e)
    

    def _internal_parse_params(self, lines):
        """
        Parse command output
        """
        result = {}

        for line in lines:
            csv = line.split(':')

            if len(csv) >= 2:
                key = csv[0].split('(')[0].strip()
                value = csv[1].strip()

                result[key] = value
            else:
                pass
        return result
