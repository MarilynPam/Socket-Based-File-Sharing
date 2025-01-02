import socket
import time
import os
from hashlib import sha256

class Client:
    def __init__(self, server_ip='127.0.0.1', server_port=9999):
        # Create a socket object using IPv4 and TCP
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server using the provided IP address and port
        self.connect_to_server(server_ip, server_port)

        #Ensure the 'Client_docs' directory exists, create the folder directory if it doesn't
        os.makedirs('Client_docs', exist_ok=True)

        self.authenticated = False
        # Performance data for network analysis
        self.performance_data = {
            'upload_rate': [],
            'download_rate': [],
            'transfer_time': []
        }
    
    def connect_to_server(self, server_ip, server_port):
        try:
            self.client.connect((server_ip, server_port))
            print(f"Connected to server at {server_ip}: {server_port}")
        except Exception as e: 
            print(f"Error connecting to server: {e}")
            exit(1)

    # Function to authenticate the user
    def authenticate(self):
        try:
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            # Hash the username and password
            hashed_username = sha256(username.encode()).hexdigest()
            hashed_password = sha256(password.encode()).hexdigest()
            # Combine hashed credentials
            creds = f"{hashed_username}:{hashed_password}"
            # Send authentication request to the server
            self.client.send(f"AUTH {creds}".encode())
            # Receive response from the server
            response = self.client.recv(1024).decode()
            if response == "Authentication successful":
                print("Login successful!")
                self.authenticated = True
            else:
                print("Authentication failed. Please try again.")
                self.authenticated = False
        except Exception as e:
            print(f"Error during authentication: {e}")
            exit(1)

    def send_command(self, command):
        try:
            # Send a command to the server
            self.client.send(command.encode())
        except Exception as e:
            print(f"Error sending command: {e}")

    def upload_file(self, filename):
        if not self.authenticated:
            print("Error: Please authenticate first.")
            return
        
        file_path = os.path.join("Client_docs", filename)
        if not os.path.exists(file_path):
            print(f"Error: File '{filename}' does not exist in 'Client_docs' folder.")
            return
        try: 
            # Send the UPLOAD command to the server
            self.send_command(f'UPLOAD {filename}')
            ack = self.client.recv(1024).decode()
            if ack != "READY":
                print(f"Error: Server not ready for upload. {ack}")
                return
            # measure start time of upload
            start_time = time.time()

            # Open the file in read-binary mode
            with open(file_path, 'rb') as file:
                while chunk := file.read(1024):
                    # Send file data to the server
                    self.client.send(chunk)
            self.client.send(b"<EOF>")
            end_time = time.time()

            print(f"File {filename} uploaded successfully")
        except Exception as e:
            print(f"Error uploading file: {e}")

    def download_file(self, filename):
        if not self.authenticated:
            print("Error: Please authenticate first first.")
            return
        try:
            # Send download command to the server
            self.send_command(f'DOWNLOAD {filename}')
            # Receive ack from the server
            ack = self.client.recv(1024).decode()
            if ack != "READY":
                print(f"Error: {ack}")
                return # Exit the function if server is not ready
            
            start_time = time.time()
            file_path = os.path.join("Client_docs", filename)
            with open(file_path, 'wb') as file:
                while True:
                    # Receive file data from the server
                    data = self.client.recv(1024)
                    if b"<EOF>" in data:
                        file.write(data.replace(b"<EOF>", b""))
                        break
                    file.write(data)
            end_time = time.time()
            transfer_time = end_time - start_time
            self.performance_data['transfer_time'].append(transfer_time)
            print(f"{filename} downloaded successfully")
        except Exception as e:
            print(f"Error downloading file: {e}")

    def delete_file(self, filename):
        if not self.authenticated:
            print("Error: Please authenticate first.")
            return
        try:
            # Send delete command to server
            self.send_command(f'DELETE {filename}')
            # Receive response from server
            response = self.client.recv(1024).decode()
            print(response)
        except Exception as e:
            print(f"Error deleting file: {e}")

    def list_files(self):
        if not self.authenticated:
            print("Error: Please authenticate first.")
            return
        try: 
            self.send_command('DIR')
            # Receive the list of files from the server
            response = self.client.recv(4096).decode()
            print(response)
        except Exception as e:
            print(f"Error listing files: {e}")

    def manage_subfolder(self, action, path):
        if not self.authenticated:
            print("Error: Please authenticate first")
            return
        try: 
            self.send_command(f'SUBFOLDER {action.upper()} {path}')
            response = self.client.recv(1024).decode()
            print(response)
        except Exception as e:
            print(f"Error managing subfolder: {e}")

    # Prompts for each command and action executable to follow
    def prompt_user(self):
        while True:
            command = input("Enter command (UPLOAD, DOWNLOAD, DELETE, DIR, SUBFOLDER, EXIT): ").strip().upper()
            if command == 'UPLOAD':
                filename = input("Enter the filename to upload: ").strip()
                self.upload_file(filename)
            elif command == 'DOWNLOAD':
                filename = input("Enter the filename to download: ").strip()
                self.download_file(filename)
            elif command == 'DELETE':
                filename = input("Enter the filename to delete: ").strip()
                self.delete_file(filename)
            elif command == 'DIR':
                self.list_files()
            elif command == 'SUBFOLDER':
                action = input("Enter action (CREATE/DELETE): ").strip().lower()
                path = input("Enter the subfolder path (add / between folders): ").strip()
                self.manage_subfolder(action, path)
            elif command == 'EXIT':
                print("Exiting...")
                break
            else:
                print("Invalid command. Please try again.")


if __name__ == "__main__":
    # Prompt user to input IP address and server port with set defaults
    ip = input("Enter server IP (default: 127.0.0.1): ").strip() or "127.0.0.1"
    port = input("Enter server port (default: 9999): ").strip() or "9999"

    # Create a new client instance with the provided IP and port
    client = Client(ip, int(port))
    # Authenticate the client
    client.authenticate()
    # If authentication is successful, prompt the user for further actions
    if client.authenticated:
        client.prompt_user()
