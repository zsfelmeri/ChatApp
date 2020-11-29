#include "MyThread.h"
#include <stdlib.h>
#include <WS2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

int main()
{
	WSADATA wsaData;
	int iResult;

	iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (iResult != NO_ERROR) {
		printf("WSAStartup() failed.\n");
		exit(1);
	}

	SOCKET ServerSocket;
	ServerSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
	if (ServerSocket == INVALID_SOCKET) {
		printf("Socket initialization failed. %ld\n", WSAGetLastError());
		WSACleanup();
		exit(1);
	}

	int port = 13001;
	struct sockaddr_in ClientAddr;
	int addrLen = sizeof(ClientAddr);

	ClientAddr.sin_family = AF_INET;
	ClientAddr.sin_port = htons(port);
	inet_pton(AF_INET, "127.0.0.1", &ClientAddr.sin_addr);

	if (bind(ServerSocket, (SOCKADDR*)&ClientAddr, sizeof(ClientAddr)) == SOCKET_ERROR) {
		printf("bind() failed.\n");
		closesocket(ServerSocket);
		WSACleanup();
		exit(1);
	}

	if (listen(ServerSocket, SOMAXCONN) == SOCKET_ERROR) {
		printf("Error listening on socket.\n");
		closesocket(ServerSocket);
		WSACleanup();
		exit(1);
	}

	std::list<std::pair<char*, MyThread*>> listOfThreads;
	SOCKET AcceptSocket;
	CRITICAL_SECTION cSection;
	InitializeCriticalSection(&cSection);

	printf("Waiting client to connect...\n");

	do {
		AcceptSocket = accept(ServerSocket, NULL, NULL);
		
		char* name = new char[255];
		iResult = recv(AcceptSocket, name, 255, 0);

		if (iResult == SOCKET_ERROR || iResult < 0) {
			printf("recv() failed. %d\n", WSAGetLastError());
		}
		else {
			name[iResult] = '\0';
			bool ok = true;
			// checks if the name exists in the list
			for (auto it : listOfThreads) {
				if (!strcmp(it.first, name)) {
					iResult = send(AcceptSocket, "nack", 4, 0);
					if (iResult == SOCKET_ERROR || iResult < 0) {
						printf("send() failed. %d\n", WSAGetLastError());
					}
					ok = false;
					break;
				}
			}

			if (ok) {
				iResult = send(AcceptSocket, "ack", 3, 0);
				if (iResult == SOCKET_ERROR || iResult < 0) {
					printf("send() failed. %d\n", WSAGetLastError());
				}
				else {
					printf("%s connected.\n", name);

					MyThread* myThread = new MyThread(AcceptSocket, &listOfThreads, &cSection);
					listOfThreads.insert(listOfThreads.end(), { name, myThread });
					myThread->start();
				}
			}
		}
	} while (AcceptSocket != INVALID_SOCKET);

	printf("Exiting...\n");

	for (auto it = listOfThreads.begin(); it != listOfThreads.end(); ++it) {
		delete[] (it->first);
		delete (it->second);
	}

	iResult = closesocket(ServerSocket);
	if (iResult == INVALID_SOCKET) {
		printf("closesocket() failed. %ld\n", WSAGetLastError());
		exit(1);
	}
	WSACleanup();

	return 0;
}