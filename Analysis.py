import os
import time
import datetime

performance_data = { #dictionary for storing all the rates and times
    'upload_rate': [],
    'download_rate': [],
    #'server_response_time': [],
    'transfer_time': []
}

def createLog():
    with open("Logs.txt", 'w') as file: #creates the file
        currentTime = datetime.datetime.now()
        file.write(f"{currentTime}: Log file created\n") #creates first line stating file was created successfully
        file.write(f"{currentTime}: Server started\n")

def serverConnect():
    with open("Logs.txt", 'a') as file: #opens Logs.txt file
        currentTime = datetime.datetime.now()
        file.write(f"{currentTime}: Server connected\n")

def clientConnect(authentication):
    with open("Logs.txt", 'a') as file: #opens Logs.txt file
        currentTime = datetime.datetime.now()
        file.write(f"{currentTime}: Client connected\n")
        if authentication:
            currentTime = datetime.datetime.now()
            file.write(f"{currentTime}: Client successfully authenticated\n")
        else:
            currentTime = datetime.datetime.now()
            file.write(f"{currentTime}: Error: Client failed authentication\n")

def timeElapsed(name, command, start, finish):
    with open("Logs.txt", 'a') as file:  # opens Logs.txt file
        if command == 'upload':
            currentTime = datetime.datetime.now()
            file.write(f"{currentTime}: Client uploaded file {name} to server")
            transfer_time = finish - start
            performance_data['transfer_time'].append(transfer_time)
            file_path = os.path.join("Server_docs", name)
            upload_rate = os.path.getsize(file_path) / transfer_time / (1024 * 1024)
            performance_data['upload_rate'].append(upload_rate)
            file.write(f": file successfully uploaded in {transfer_time} seconds at a rate of {upload_rate} Mbps\n")

        if command == 'download':
            currentTime = datetime.datetime.now()
            file.write(f"{currentTime}: Client downloaded file {name} from server")
            transfer_time = finish - start
            performance_data['transfer_time'].append(transfer_time)
            file_path = os.path.join("Server_docs", name)
            download_rate = os.path.getsize(file_path) / transfer_time / (1024 * 1024)
            performance_data['download_rate'].append(download_rate)
            file.write(f": file successfully downloaded in {transfer_time} seconds at a rate of {download_rate} Mbps\n")




def error(commandAttempted, error):
    with open("Logs.txt", 'a') as file:
        if commandAttempted == 'download':
            currentTime = datetime.datetime.now()
            file.write(f"{currentTime}: Download requested from client:")
            if error == 'server':
                file.write(" Server was not ready\n")
            elif error == 'file not found':
                file.write(" file not found\n")
            else:
                file.write(" Client failed to download file\n")

        if commandAttempted == 'upload':
            currentTime = datetime.datetime.now()
            file.write(f"{currentTime}: Upload requested from client: error during file upload\n")

        if commandAttempted == 'subfolder':
            if error == 'subfolder nonexistent':
                currentTime = datetime.datetime.now()
                file.write(f"{currentTime}: Subfolder requested for deletion by client does not exist\n")
            elif error == 'invalid action':
                currentTime = datetime.datetime.now()
                file.write(f"{currentTime}: Subfolder action requested by client does not exist\n")
            else:
                currentTime = datetime.datetime.now()
                file.write(f"{currentTime}: Error managing subfolder\n")

        if commandAttempted == 'file list':
            currentTime = datetime.datetime.now()
            file.write(f"{currentTime}: Error: Server could not retrieve file list\n")


def command(command): #meant for the commands that don't require a time
    with open("Logs.txt", 'a') as file:
        if command == 'subfolder create':
            currentTime = datetime.datetime.now()
            file.write(f"{currentTime}: Subfolder created\n")

        elif command == 'subfolder delete':
            currentTime = datetime.datetime.now()
            file.write(f"{currentTime}: Subfolder deleted\n")

        elif command == 'file list':
            currentTime = datetime.datetime.now()
            file.write(f"{currentTime}: Files listed to client\n")

        elif command == 'delete file':
            currentTime = datetime.datetime.now()
            file.write(f"{currentTime}: File deleted\n")

def clientDisconnected():
    with open("Logs.txt", 'a') as file:
        currentTime = datetime.datetime.now()
        file.write(f"\n{currentTime}: Client disconnected from server\n")
        totalDownloads = len(performance_data['download_rate'])
        sumDownload = sum(performance_data['download_rate'])
        avgDownload = sumDownload / totalDownloads
        file.write(f"Files downloaded by client: {totalDownloads}\n")
        file.write(f"Average Download Rate: {avgDownload}\n Mbps")
        totalUploads = len(performance_data['upload_rate'])
        sumUpload = sum(performance_data['upload_rate'])
        avgUpload = sumUpload / totalUploads
        file.write(f"Files uploaded by client: {totalUploads}\n")
        file.write(f"Average Upload Rate: {avgUpload}\n Mbps")
        avgTransfer = sum(performance_data['transfer_time']) / len(performance_data['transfer_time'])
        file.write(f"Average Transfer Time Rate: {avgTransfer}\n Mbps")
        #avgResponse = sum(performance_data['server_response_time']) / len(performance_data['server_response_time'])
        #file.write(f"Average Server Response Time Rate: {avgResponse}\n")



# logs created, server connected, client connected, functions as they go by, averages displayed when client disconnects
