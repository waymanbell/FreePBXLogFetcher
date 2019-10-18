import paramiko

def fetch_asterisk_logs():
    pass

def fetch_provisioning_logs():
    pass

def fetch_html_logs():
    pass

def fetch_mail_logs():
    pass


startflag = 0
#Prompt for FreePBX host and credentials from which to grab logs
while startflag == 0:
    usersubmittedhostname = input("FQDN or IP: ")
    rootpw = input("Password for 'root': ")

#Create connection to FreePBX host
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname = usersubmittedhostname, port = 22, username = 'root', password = rootpw, timeout = 5.0)
        startflag = 1
    except:
        print("Connection timed out.\n")
        startflag = 0
queryforlogtype = input("Log type to query: (1) Asterisk, (2) Provisioning, (3) HTML, (4) Mail -- Enter any combination on one line\n")
additionalsearchtermsflag = 0
searchlogsfor = []
while additionalsearchtermsflag == 0:
    searchlogsfor.append(input("What term are you searching for? Search term is case sensitive, enter 'all' for unfiltered log files\n"))
    if str(input("Search for additional terms? (y/n): ")).lower()=='y':
        continue
    else:
        additionalsearchtermsflag=1
print("Beginning fetch...")
try:
    if '1' in queryforlogtype:
        #Grab list of files in log directory
        stdin,stdout,stderr=client.exec_command("ls /var/log/asterisk")
        remotefilelist=stdout.readlines()

        #Download log files, strip away all messages beyond 'Unreachable' and 'Reachable', save to C:\temp\
        ftp_client = client.open_sftp()
        if 'Windows' in platform.system():
            localfilelocation = 'c:\\temp\\'
        elif 'Darwin' in platform.system():
            localfilelocation = '/Library/Temp/'
        for each in remotefilelist:
            if 'full' in each:
                remotefilename = '/var/log/asterisk/' + each[:-1]
                localfilename = localfilelocation + each[:-1]
                ftp_client.get(remotefilename, localfilename)
                print('Downloading file: ' + remotefilename + '\n\tLocal file @ ' + localfilename)
                print('Parsing ' + localfilename + '...')
                logfile = open(localfilename, 'r')
                parsedlogfile = open(localfilename + '_parsed.txt', 'w+')
                for everyline in logfile:
                    for eachterm in searchlogsfor:
                        if eachterm in everyline or str(eachterm).lower() == 'all':
                            parsedlogfile.write(everyline)
                logfile.close()
                parsedlogfile.close()
                print('Cleaned file can be found @ ' + localfilename + '_parsed.txt\n')
except:
    print("There was a problem. Attempting to gracefully close")

ftp_client.close()
client.close()

input('Process complete. Press enter to close.')
