#include "MyThread.h"

MyThread::MyThread(SOCKET socket, std::list<std::pair<std::pair<char*, std::vector<char*>>, MyThread*>>* listOfThreads, CRITICAL_SECTION* critSection) : m_socket(socket), m_listOfThreads(listOfThreads), m_criticalSection(critSection) {}

MyThread::~MyThread() {}

void MyThread::run(void) {
	char* myName = new char[255];
	bool exiting = false;
	int iResult;
	char* RcvBuf = new char[36567];

	strcpy(myName, m_listOfThreads->back().first.first);
	for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
		if (!strcmp(it->first.first, "asd") || !strcmp(it->first.first, "dsa")) {
			char buff[] = "Kings";
			it->first.second.push_back(buff);
		}
	}

	//Update list of users
	std::vector<char*> usersList;
	for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
		usersList.push_back(it->first.first);
	}

	char* SendBuf = new char[781];
	int type = 4;
	char* tmp = new char[256];
	for (int i = 0; i < 255; ++i) {
		tmp[i] = '*';
	}
	tmp[255] = '\0';
	for (auto it : usersList) {
		sprintf(SendBuf, "%d %s %s %s", type, tmp, tmp, it);
		for (auto it2 = m_listOfThreads->begin(); it2 != m_listOfThreads->end(); ++it2) {
			//EnterCriticalSection(&(*m_criticalSection));
			
			iResult = send(it2->second->m_socket, SendBuf, strlen(SendBuf), 0);
			Sleep(100);

			//LeaveCriticalSection(&(*m_criticalSection));

			if (iResult == SOCKET_ERROR || iResult < 0) {
				goto disconnect;
			}
		}
	}
	sprintf(SendBuf, "%d %s %s %s", type, tmp, tmp, "CTS");
	for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
		iResult = send(it->second->m_socket, SendBuf, strlen(SendBuf), 0);
		if (iResult == SOCKET_ERROR || iResult < 0) {
			goto disconnect;
		}
	}
	delete[] tmp;
	delete[] SendBuf;
	usersList.clear();

	//Server logic
	do {
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

		exiting = false;
		iResult = recv(m_socket, RcvBuf, 36567, 0);
		if (iResult == SOCKET_ERROR || iResult < 0) {
			//printf("recv() failed. %d\n", WSAGetLastError());
			exiting = true;
		}
		else {
			RcvBuf[(iResult > 36567)? 36567 : iResult] = '\0';
			char from[255], to[255], msg[36056];
			sscanf(RcvBuf, "%d %s %s %s", &type, to, from, msg);

			//Private message
			if (type == 1) {
				for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
					if (!strcmp(it->first.first, to)) {
						iResult = send(it->second->m_socket, RcvBuf, strlen(RcvBuf), 0);
						if (iResult == SOCKET_ERROR || iResult < 0) {
							printf("send() failed. %d\n", WSAGetLastError());
							exiting = true;
						}
						break;
					}
				}
			}
			//Group message
			else if (type == 2) {
				for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
					if (strcmp(it->first.first, myName)) {
						for (auto group : it->first.second) {
							if (!strcmp(group, to)) {
								iResult = send(it->second->m_socket, RcvBuf, strlen(RcvBuf), 0);
								if (iResult == SOCKET_ERROR || iResult < 0) {
									printf("send() failed. %d\n", WSAGetLastError());
									exiting = true;
								}
								break;
							}
						}
					}
				}
			}
			//Send file
			else if (type == 3) {

			}
		}

	} while (m_socket != SOCKET_ERROR && !exiting);

disconnect:
	printf("%s disconnected.\n", myName);
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
	delete[] myName;
	delete[] RcvBuf;

	//Update list of users
	//for (auto iter = m_listOfThreads->begin(); iter != m_listOfThreads->end(); ++iter) {
	//	usersList.push_back(iter->first);
	//}

	//SendBuf = new char[781];
	//type = 4;
	//tmp = new char[256];
	//for (int i = 0; i < 255; ++i) {
	//	tmp[i] = '*';
	//}
	//tmp[255] = '\0';
	//for (auto iter : usersList) {
	//	sprintf(SendBuf, "%d %s %s %s", type, tmp, tmp, iter);
	//	for (auto iter2 = m_listOfThreads->begin(); iter2 != m_listOfThreads->end(); ++iter2) {
	//		//EnterCriticalSection(&(*m_criticalSection));

	//		iResult = send(iter2->second->m_socket, SendBuf, strlen(SendBuf), 0);
	//		Sleep(100);

	//		//LeaveCriticalSection(&(*m_criticalSection));

	//		if (iResult == SOCKET_ERROR || iResult < 0) {
	//			printf("send() failed. %d\n", WSAGetLastError());
	//		}
	//	}
	//}
	//sprintf(SendBuf, "%d %s %s %s", type, tmp, tmp, "CTS");
	//for (auto iter = m_listOfThreads->begin(); iter != m_listOfThreads->end(); ++iter) {
	//	iResult = send(iter->second->m_socket, SendBuf, strlen(SendBuf), 0);
	//	if (iResult == SOCKET_ERROR || iResult < 0) {
	//		printf("send() failed. %d\n", WSAGetLastError());
	//	}
	//}
	//delete[] tmp;
	//delete[] SendBuf;
}