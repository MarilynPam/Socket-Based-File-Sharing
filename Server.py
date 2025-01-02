import shutil
import Analysis
import socket
import threading
import os
import time
from hashlib import sha256

from Analysis import createLog

# Predefined user credentials for authentication
USER_CREDENTIALS = {
    sha256("user1".encode()).hexdigest() : sha256("password1".encode()).hexdigest(),
    sha256("user2".encode()).hexdigest() : sha256("password2".encode()).hexdigest(),
}

# function to delete files in a subfolder recursively as the delete in subfolder only deletes empty subfolders
def remove_directory_tree(start_directory: str):
    # Iterate over all the entries in the directory
    for name in os.listdir(start_directory):
        path = os.path.join(start_directory, name)
        # Create full path to the entry
        if os.path.isfile(path):
            os.remove(path) #remove the file if it is a file
        else:
            remove_directory_tree(path) #recursively call the function if it is a directory
    os.rmdir(start_directory) # Remove the now empty directory

class Server:
    def __init__(self, host='0.0.0.0', port=9999):
        # Create a socket object using IPv4 and TCP
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the specified host and port
        self.server.bind((host, port))
        # Listen for incoming connections (up to 5 clients)
        self.server.listen(5)
        print(f"Server listening on {host}:{port}")

        #Ensure the 'Server_docs' directory exists, create the folder directory if it doesn't
        os.makedirs('Server_docs', exist_ok=True)

        # Initialize a list to keep track of connected clients
        self.clients = []
        # Initialize a dictionary to store performance data for network analysis
        self.performance_data = {
            'upload_rate': [],
            'download_rate': [],
            'transfer_time': []
        }

    def handle_client(self, client_socket):
        authenticated = False
        try:
            # Handle client requests in a loop
            while True:
                # Receive request from client
                request = client_socket.recv(1024).decode()
                if not request:
                    break
                #Split the request into command and arguments
                command, *args = request.split()
                if command == "AUTH":
                    # Extract username and hashed password from arguments
                    username, hashed_password = args[0].split(":")
                    # Check if the credentials match the stored credentials
                    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == hashed_password:
                        client_socket.send(b"Authentication successful")
                        authenticated = True
                        Analysis.clientConnect(True)
                        print(f"Client {username} authenticated successfully.")
                    else:
                        client_socket.send(b"Authentication failed")
                        Analysis.clientConnect(False)
                        print(f"Client {username} failed authentication.")
                    continue

                if not authenticated:
                    client_socket.send(b"Error: Please authenticate first.")
                    continue

                # Process commands
                if command == 'UPLOAD':
                    self.upload_file(client_socket, args[0])
                elif command == 'DOWNLOAD':
                    self.download_file(client_socket, args[0])
                elif command == 'DELETE':
                    self.delete_file(client_socket, args[0])
                elif command == 'DIR':
                    self.list_files(client_socket)
                elif command == 'SUBFOLDER':
                    self.manage_subfolder(client_socket, args[0], args[1])
                else:
                    client_socket.send(b"Error: unknown command")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()
            Analysis.clientDisconnected()
            print("Connection closed.")

    def upload_file(self, client_socket, filename):
        file_path = os.path.join('Server_docs', filename)
        try:
            client_socket.send(b"READY")
            start_time = time.time()
            with open(file_path, 'wb') as file:
                while True:
                    # Receive data in chunks
                    data = client_socket.recv(1024)
                    if b"<EOF>" in data:
                        file.write(data.replace(b"<EOF>", b""))
                        break
                    # Write data to the file
                    file.write(data)
            # Measure the end time of the upload
            end_time = time.time()
            # Calculate the transfer time
            transfer_time = end_time - start_time
            # Store the transfer time in the performance data
            Analysis.timeElapsed(filename, 'upload', start_time, end_time)
            self.performance_data['transfer_time'].append(transfer_time)
            print(f"File {filename} uploaded successfully in {transfer_time:.2f} seconds")
        except Exception as e:
            print(f"Error during file upload: {e}")
            Analysis.error('upload', 'error during file upload')
            client_socket.send(b"Error: Upload failed")


    def download_file(self, client_socket, filename):
        # Measure the start time of the download
        start_time = time.time()

        #define the file path
        file_path = os.path.join('Server_docs', filename)
        if not os.path.exists(file_path):
            client_socket.send(b"ERROR: File not found")
            Analysis.error('download', 'file not found')
            return

        try:
            client_socket.send(b"READY")
            # Open the file in read-binary mode
            with open(file_path, 'rb') as file:
                while chunk := file.read(1024):
                    # Send data to the client
                    client_socket.send(chunk)
                client_socket.send(b"<EOF>")
                # Measure the end time of the download
                end_time = time.time()
                # Calculate the transfer time
                transfer_time = end_time - start_time
                # Store the transfer time in the performance data
                self.performance_data['transfer_time'].append(transfer_time)
                Analysis.timeElapsed(filename, 'download', start_time, end_time)
                print(f"File {filename} downloaded successfully in {transfer_time:.2f} seconds")
        except Exception as e:
            print(f"Error during file download: {e}")
            # Send an error message if the file does not exist
            client_socket.send(b"ERROR: Download failed")
            Analysis.error('download', 'failed')

    def delete_file(self, client_socket, filename):
        file_path = os.path.join('Server_docs', filename)
        # Check if the file exists
        if not os.path.exists(file_path):
            client_socket.send(b"Error: File '{filename}' not found".encode())
            print(f"Error: File '{filename}' not found")
            Analysis.error('delete file', 'file not found')
            return
        try:
            os.remove(file_path)
            print(f"File '{filename}' deleted successfully")
            Analysis.command('delete file')
            client_socket.send(f"File '{filename}' deleted successfully".encode())
        except Exception as e:
            print(f"Error deleting file: {e}")
            Analysis.error('delete file', 'error')
            client_socket.send(b"ERROR: Failed to delete file '{filename}'".encode())

    def list_files(self, client_socket):
        try:
            # List all the files in the current directory
            files = os.listdir('Server_docs')
            file_list = '\n'.join(files) if files else "No files available."
            # Send the list of files to the client
            client_socket.send(file_list.encode())
            Analysis.command('file list')
        except Exception as e:
            print(f"Error listing files: {e}")
            client_socket.send(b"ERROR: Could not retrieve file list")
            Analysis.error('file list', 'could not retrieve list')

    def manage_subfolder(self, client_socket, action, path):
        subfolder_path = os.path.join('Server_docs', path)
        try:
            # Handle subfolder creation
            if action == 'CREATE':
                os.makedirs(subfolder_path, exist_ok=True)
                client_socket.send(b"Subfolder created successfully")
                print(f"Subfolder '{path}' created.")
                Analysis.command('subfolder create')
            # Handle subfolder deletion and call remove_directory_tree function
            elif action == 'DELETE':
                if os.path.exists(subfolder_path):
                    remove_directory_tree(subfolder_path)
                    client_socket.send(b"Subfolder deleted successfully")
                    print(f"Subfolder '{path}' and its contents deleted.")
                    Analysis.command('subfolder delete')
                else:
                    client_socket.send(b"ERROR: Subfolder not found")
                    print(f"Error: Subfolder '{path}' does not exist.")
                    Analysis.error('subfolder', 'subfolder nonexistent')
            else:
                client_socket.send(b"ERROR: Invalid subfolder action")
                print(f"Error: invalid action '{action}' for subfolder.")
                Analysis.error('subfolder', 'invalid action')
        except Exception as e:
            print(f"Error managing subfolder '{path}': {e}")
            client_socket.send(f"ERROR: subfolder operation failed: {e}".encode())
            Analysis.error('subfolder', 'error managing subfolder')

    def start(self):
        # Start the server to accept client connections
        while True:
            # Accept a new client connection
            client_socket, addr = self.server.accept()
            print(f"Accepted connection from {addr}")
            # Create a new thread to handle the client
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()
            Analysis.serverConnect()

if __name__ == "__main__":
    # Create and start the server
    server = Server()
    Analysis.createLog()
    server.start()