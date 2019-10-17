import paramiko

#Prompt for FreePBX host and credentials from which to grab logs
usersubmittedhostname = input("FQDN or IP: ")
rootpw = input("Password for 'root': ")

#Create connection to FreePBX host
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname = usersubmittedhostname, port = 22, username = 'root', password = rootpw)

#Grab list of files in log directory
stdin,stdout,stderr=client.exec_command("ls /var/log/asterisk")
remotefilelist=stdout.readlines()

#Download log files, strip away all messages beyond 'Unreachable' and 'Reachable', save to C:\temp\
ftp_client=client.open_sftp()
for each in remotefilelist:
    if 'full' in each:
        remotefilename = '/var/log/asterisk/'+each[:-1]
        localfilename = 'c:\\temp\\'+each[:-1]
        ftp_client.get(remotefilename, localfilename)
        print('Downloading file: ' + remotefilename + '\n\tLocal file @ ' + localfilename)
        print('Parsing ' + localfilename + '...')
        logfile = open(localfilename, 'r')
        parsedlogfile = open(localfilename+'_parsed.txt', 'w+')
        for everyline in logfile:
            if 'Unreachable' in everyline or 'Reachable' in everyline:
                parsedlogfile.write(everyline)
        logfile.close()
        parsedlogfile.close()
        print('Cleaned file can be found @ ' + localfilename + '_parsed.txt\n')

ftp_client.close()
client.close()

input('Process complete. Press enter to close.')
