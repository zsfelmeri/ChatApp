#include "MyThread.h"

MyThread::MyThread(SOCKET socket, std::list<std::pair<std::pair<char*, std::vector<char*>>, MyThread*>>* listOfThreads, CRITICAL_SECTION* critSection) : m_socket(socket), m_listOfThreads(listOfThreads), m_criticalSection(critSection) {}

MyThread::~MyThread() {}

void MyThread::run(void) {
	char* myName = new char[255];
	bool exiting = false;
	int iResult;
	char* RcvBuf = new char[36567];

	strcpy(myName, m_listOfThreads->back().first.first);

	//Update list of users
	updateUsersList();

	//Server logic
	do {
		EnterCriticalSection(&(*m_criticalSection));
		auto it = m_listOfThreads->begin();
		while(it != m_listOfThreads->end()) {
			if (!it->second->isRunning() && it->second->isExited()) {
				auto temp = *it;
				if (it == m_listOfThreads->begin()) {
					m_listOfThreads->erase(it);
				}
				else {
					m_listOfThreads->erase(it--);
				}
				delete[] temp.first.first;
				delete[] temp.second;
			}
			++it;
		}
		LeaveCriticalSection(&(*m_criticalSection));

		exiting = false;
		iResult = recv(m_socket, RcvBuf, 36567, 0);
		if (iResult == SOCKET_ERROR || iResult < 0) {
			//printf("recv() failed. %d\n", WSAGetLastError());
			exiting = true;
		}
		else {
			RcvBuf[(iResult > 36566)? 36566 : iResult] = '\0';
			char from[255], to[255], msg[36056];
			int type;
			sscanf(RcvBuf, "%d %s %s %s", &type, to, from, msg);

			//Private message
			if (type == 1) {
				EnterCriticalSection(&(*m_criticalSection));
				for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
					if (!strcmp(it->first.first, to)) {
						iResult = send(it->second->m_socket, RcvBuf, (int)strlen(RcvBuf), 0);
						if (iResult == SOCKET_ERROR || iResult < 0) {
							exiting = true;
						}
						break;
					}
				}
				LeaveCriticalSection(&(*m_criticalSection));
			}
			//Group message
			else if (type == 2) {
				EnterCriticalSection(&(*m_criticalSection));
				for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
					if (strcmp(it->first.first, myName)) {
						for (auto group : it->first.second) {
							if (!strcmp(group, to)) {
								iResult = send(it->second->m_socket, RcvBuf, (int)strlen(RcvBuf), 0);
								if (iResult == SOCKET_ERROR || iResult < 0) {
									exiting = true;
								}
								break;
							}
						}
					}
				}
				LeaveCriticalSection(&(*m_criticalSection));
			}
			//Send file
			else if (type == 3) {
				EnterCriticalSection(&(*m_criticalSection));
				for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
					if (!strcmp(it->first.first, to)) {
						while (strcmp(RcvBuf, "Done")) {
							iResult = send(it->second->m_socket, RcvBuf, (int)strlen(RcvBuf), 0);
							if (iResult == SOCKET_ERROR || iResult < 0) {
								goto disconnect;
							}

							iResult = recv(m_socket, RcvBuf, 36051, 0);
							if (iResult == SOCKET_ERROR || iResult < 0) {
								goto disconnect;
							}
							RcvBuf[(iResult > 36051) ? 36051 : iResult] = '\0';
						}

						iResult = send(it->second->m_socket, RcvBuf, (int)strlen(RcvBuf), 0);
						if (iResult == SOCKET_ERROR || iResult < 0) {
							goto disconnect;
						}
						break;
					}
				}
				LeaveCriticalSection(&(*m_criticalSection));
			}
			//Update list of groups (new group created)
			else if (type == 5) {
				EnterCriticalSection(&(*m_criticalSection));
				for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
					if (strcmp(it->first.first, myName)) {
						iResult = send(it->second->m_socket, RcvBuf, (int)strlen(RcvBuf), 0);
						if (iResult == SOCKET_ERROR || iResult < 0) {
							goto disconnect;
						}
					}
				}
				LeaveCriticalSection(&(*m_criticalSection));
			}
			//Join to a group
			else if (type == 6) {
				EnterCriticalSection(&(*m_criticalSection));
				for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
					if (!strcmp(it->first.first, myName)) {
						it->first.second.push_back(to);
						break;
					}
				}
				LeaveCriticalSection(&(*m_criticalSection));
			}
		}

	} while (m_socket != SOCKET_ERROR && !exiting);

disconnect:
	printf("%s disconnected.\n", myName);

	//EnterCriticalSection(&(*m_criticalSection));
	auto it = m_listOfThreads->begin();
	while(it != m_listOfThreads->end()) {
		if (!strcmp(it->first.first, myName)) {
			auto temp = *it;
			if (it == m_listOfThreads->begin()) {
				m_listOfThreads->erase(it);
			}
			else {
				m_listOfThreads->erase(it--);
			}
			delete[] temp.first.first;
			delete temp.second;
			break;
		}
		++it;
	}
	//LeaveCriticalSection(&(*m_criticalSection));
	delete[] myName;
	delete[] RcvBuf;

	//Update list of users
	//updateUsersList();
}

void MyThread::updateUsersList() {
	std::vector<char*> usersList;
	for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
		usersList.push_back(it->first.first);
	}
	int iResult;

	char *SendBuf = new char[781];
	int type = 4;
	char *tmp = new char[256];
	for (int i = 0; i < 255; ++i) {
		tmp[i] = '*';
	}
	tmp[255] = '\0';

	EnterCriticalSection(&(*m_criticalSection));
	for (auto it : usersList) {
		sprintf(SendBuf, "%d %s %s %s", type, tmp, tmp, it);
		for (auto it2 = m_listOfThreads->begin(); it2 != m_listOfThreads->end(); ++it2) {

			iResult = send(it2->second->m_socket, SendBuf, (int)strlen(SendBuf), 0);
			Sleep(100);

			if (iResult == SOCKET_ERROR || iResult < 0) {
				printf("send() failed. %d\n", WSAGetLastError());
			}
		}
	}
	LeaveCriticalSection(&(*m_criticalSection));

	sprintf(SendBuf, "%d %s %s %s", type, tmp, tmp, "CTS");
	EnterCriticalSection(&(*m_criticalSection));
	
	for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
		iResult = send(it->second->m_socket, SendBuf, (int)strlen(SendBuf), 0);
		if (iResult == SOCKET_ERROR || iResult < 0) {
			printf("send() failed. %d\n", WSAGetLastError());
		}
	}

	LeaveCriticalSection(&(*m_criticalSection));
	delete[] tmp;
	delete[] SendBuf;
}