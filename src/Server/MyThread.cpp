#include "MyThread.h"

MyThread::MyThread(SOCKET socket, std::list<std::pair<char*, MyThread*>>* listOfThreads, CRITICAL_SECTION* critSection) : m_socket(socket), m_listOfThreads(listOfThreads), m_criticalSection(critSection) {}

MyThread::~MyThread() {}

void MyThread::run(void) {
	char* str = new char[255];
	bool exiting = false;
	int iResult;
	char* RcvBuf = new char[36567];

	strcpy(str, m_listOfThreads->back().first);
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
				delete[] temp.first;
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
			int type;
			char from[255], to[255], msg[36056];
			sscanf(RcvBuf, "%d %s %s %s", &type, to, from, msg);

			//Private message
			if (type == 1) {
				for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
					if (!strcmp(it->first, to)) {
						iResult = send(m_socket, RcvBuf, strlen(RcvBuf), 0);
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

			}
			//Send file
			else if (type == 3) {

			}
			//Update list of users
			else if (type == 4) {

			}
		}

	} while (m_socket != SOCKET_ERROR && !exiting);

	printf("%s disconnected.\n", str);
	auto it = m_listOfThreads->begin();
	while(it != m_listOfThreads->end()) {
		if (!strcmp(it->first, str)) {
			auto temp = *it;
			if (it == m_listOfThreads->begin()) {
				m_listOfThreads->erase(it);
			}
			else {
				m_listOfThreads->erase(it--);
			}
			delete temp.first;
			delete temp.second;
			break;
		}
		++it;
	}
	delete[] str;
	delete[] RcvBuf;

	/*strcpy_s(SendBuf, "Hello!\n .........\nHave a nice day!\n");
	int len = strlen(SendBuf);

	m_listOfThreads->remove_if([](const auto& it) {
		return !it->isRunning() && it->isExited();
		});

	for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
		EnterCriticalSection(&(*m_criticalSection));

		int res = send(this->m_socket, SendBuf, len, 0);

		LeaveCriticalSection(&(*m_criticalSection));

		if (res == SOCKET_ERROR || res < 0) {
			printf("send() failed. %d\n", WSAGetLastError());
			exit(1);
		}
	}*/
}