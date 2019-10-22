import os, paramiko, platform


def fetch_asterisk_logs(client, searchterms):
    if not os.path.exists(os.getcwd() + '\\asterisk'):
        os.mkdir(os.getcwd() + '\\asterisk')
    os.chdir(os.getcwd() + '\\asterisk')

    stdin, stdout, stderr = client.exec_command("ls /var/log/asterisk")
    remotefilelist = stdout.readlines()
    ftp_client = client.open_sftp()
    for each in remotefilelist:
        if 'full' in each:
            remotefilename = '/var/log/asterisk/' + each[:-1]
            localfilename = os.getcwd() + '\\' + each[:-1]
            ftp_client.get(remotefilename, localfilename)
            print('Downloading file: ' + remotefilename + '\n\tLocal file @ ' + localfilename)
            print('Parsing ' + localfilename + '...')
            parselogs(localfilename, searchterms)
    ftp_client.close()


def fetch_provisioning_logs(client, searchterms):
    if not os.path.exists(os.getcwd() + '\\provisioning_ftp'):
        os.mkdir(os.getcwd() + '\\provisioning_ftp')
    os.chdir(os.getcwd() + '\\provisioning_ftp')

    stdin, stdout, stderr = client.exec_command("ls /var/log")
    remotefilelist = stdout.readlines()
    ftp_client = client.open_sftp()
    for each in remotefilelist:
        if 'messages' in each:
            remotefilename = '/var/log/' + each[:-1]
            localfilename = os.getcwd() + '\\' + each[:-1]
            ftp_client.get(remotefilename, localfilename)
            print('Downloading file: ' + remotefilename + '\n\tLocal file @ ' + localfilename)
            print('Parsing ' + localfilename + '...')
            parselogs(localfilename, searchterms)
    ftp_client.close()


def fetch_http_logs(client, searchterms):
    if not os.path.exists(os.getcwd() + '\\http'):
        os.mkdir(os.getcwd() + '\\http')
    os.chdir(os.getcwd() + '\\http')

    stdin, stdout, stderr = client.exec_command("ls /var/log/httpd")
    remotefilelist = stdout.readlines()
    ftp_client = client.open_sftp()
    for each in remotefilelist:
        if 'log' in each:
            remotefilename = '/var/log/httpd/' + each[:-1]
            localfilename = os.getcwd() + '\\' + each[:-1]
            ftp_client.get(remotefilename, localfilename)
            print('Downloading file: ' + remotefilename)
            print('\tLocal file @ ' + localfilename)
            print('\tParsing ' + localfilename + '...')
            parselogs(localfilename, searchterms)
    ftp_client.close()


def fetch_mail_logs(client, searchterms):
    if not os.path.exists(os.getcwd() + '\\mail'):
        os.mkdir(os.getcwd() + '\\mail')
    os.chdir(os.getcwd() + '\\mail')

    stdin, stdout, stderr = client.exec_command("ls /var/mail")
    remotefilelist = stdout.readlines()
    ftp_client = client.open_sftp()
    for each in remotefilelist:
        if 'asterisk' in each:
            remotefilename = '/var/mail/' + each[:-1]
            localfilename = os.getcwd() + '\\' + each[:-1]
            ftp_client.get(remotefilename, localfilename)
            print('Downloading file: ' + remotefilename + '\n\tLocal file @ ' + localfilename)
            print('Parsing ' + localfilename + '...')
            parselogs(localfilename, searchterms)
    ftp_client.close()


def parselogs(localfilename, searchterms):
    logfile = open(localfilename, 'r')
    parsedlogfile = open(localfilename + '_parsed.txt', 'w+')
    for everyline in logfile:
        for eachterm in searchlogsfor:
            if eachterm in everyline or str(eachterm).lower() == 'all':
                parsedlogfile.write(everyline)
    logfile.close()
    parsedlogfile.close()
    print('Cleaned file can be found @ ' + localfilename + '_parsed.txt\n')


def loadtargets(pbxlist):
    names = []
    hostips = []
    passwords = []

    for line in pbxlist:
        line = line.split(',')
        names.append(line[0])
        hostips.append(line[1])
        passwords.append(line[2])

    return names, hostips, passwords

username = os.getlogin()
if platform.system() == 'Windows':
    pbxhostslist = open('c:\\Users\\' + username + '\\Desktop\\PBXHosts.txt', 'r')
else:
    exit()
filecontents = pbxhostslist.readlines()
hostnamelist, iplist, passlist = loadtargets(filecontents)

for eachpass in range(len(passlist)):
    if '\n' in passlist[eachpass]:
        passlist[eachpass] = passlist[eachpass][:-1]

additionalsearchtermsflag = 1
searchlogsfor = []
while additionalsearchtermsflag:
    searchlogsfor.append(input("What term are you searching for? Search term is case sensitive, enter 'all' for unfiltered log files\n"))
    if str(input("Search for additional terms? (y/n): ")).lower() == 'y':
        continue
    else:
        additionalsearchtermsflag = 0

for eachhost in range(len(hostnamelist)):
    if platform.system() == 'Windows':
        localpath = 'c:\\Users\\' + os.getlogin() + '\\Desktop\\PBXLogs\\'

    if not os.path.exists(localpath + hostnamelist[eachhost]):
        os.makedirs(localpath + hostnamelist[eachhost])
    os.chdir(localpath + hostnamelist[eachhost])
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname = iplist[eachhost], port = 22, username = 'root',
                   password = passlist[eachhost])

    print("Beginning fetch...")
    fetch_asterisk_logs(client, searchlogsfor)
    os.chdir('c:\\Users\\Wayman\\Desktop\\PBXLogs\\'+hostnamelist[eachhost])
    fetch_http_logs(client, searchlogsfor)
    os.chdir('c:\\Users\\Wayman\\Desktop\\PBXLogs\\'+hostnamelist[eachhost])
    fetch_mail_logs(client, searchlogsfor)
    os.chdir('c:\\Users\\Wayman\\Desktop\\PBXLogs\\'+hostnamelist[eachhost])
    fetch_provisioning_logs(client, searchlogsfor)
    client.close()
