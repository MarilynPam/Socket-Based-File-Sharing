# Socket-Based-File-Sharing
A simple file sharing system based on a server-client architecture using Python

## Project Description
This project implements a distributed file-sharing system based on a server-client architecture. It aims to provide a secure and fully capable method of sharing and managing files across various computers in a network. Multiple clients can receive and send files to one server, all on separate computers. 
The file-sharing system is built in Python, using network protocols such as TCP for reliable and multithreaded communication to the server. Functionally, the system connects to the server, authenticates users, and allows clients to upload or download files, list files and directories and manage subfolders through a user interface. Security measures include user authentication with username and password input. The interface allows users to select commands and send requests to the server, with error messages and informative feedback provided to indicate the status of file transfers and operations. Performance data, including file transfer rates and times, is collected to provide insight into the system's efficacy through the analysis.py. Performance metrics are also provided by running tests of various loads on the client-side of the program.

## Implementation Details
### Client.py
- **Libraries Used**: `socket`, `os`, `hashlib`, `sys`
- **Functionality**: Authenticates users, manages files, and interacts with server directories.
- **Security**: Uses `sha256` for hashing usernames and passwords.
- **File Transfers**: Implements chunk-based file transfers (1024-byte chunks).
- **Initialization**: Creates a socket using IPv4 (AF_INET) and TCP (SOCK_STREAM), connects to the server, and ensures a local directory exists for file storage.
- **Commands**:
  - **UPLOAD**: Verifies file existence, sends the UPLOAD command, and transfers the file in chunks.
  - **DOWNLOAD**: Sends the DOWNLOAD command, receives the file in chunks, and saves it locally.
  - **DELETE**: Sends the DELETE command and prints the server's response.
  - **DIR**: Sends the DIR command and displays the list of files.
  - **SUBFOLDER**: Sends the SUBFOLDER command to create or delete subfolders and prints the server's response.

### Server.py
- **Libraries Used**: `socket`, `threading`, `os`, `hashlib`, `shutil`, `sys`
- **Functionality**: Handles multiple clients concurrently using threads, manages the Server_docs directory, and processes client commands.
- **Initialization**: Creates a socket using IPv4 and TCP, binds the server to the specified host and port, and ensures the Server_docs directory exists.
- **Commands**:
  - **AUTH**: Authenticates clients using hashed credentials.
  - **UPLOAD**: Sends a READY acknowledgment, receives the file in chunks, and saves it.
  - **DOWNLOAD**: Checks file existence, sends a READY acknowledgment, and transfers the file in chunks.
  - **DELETE**: Verifies file existence, deletes the file, and sends a response.
  - **DIR**: Retrieves and sends the list of files.
  - **SUBFOLDER**: Handles CREATE and DELETE commands for subfolders.

### Analysis.py
- **Functionality**: Documents rates and times of server interactions.
- **Performance Data**: Stores upload rates, download rates, and transfer times.
- **Logging**: Creates a log file with timestamps for server start, client connections, file transfers, errors, and client disconnections.

## Getting Started
1. Clone the repository.
2. Install the required libraries.
3. Run `server.py` on the server machine.
4. Run `client.py` on the client machines.
5. Follow the prompts to authenticate and use the file-sharing system.
