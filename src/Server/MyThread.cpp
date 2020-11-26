#include "MyThread.h"

MyThread::MyThread(SOCKET socket, std::list<std::pair<char*, MyThread*>>* listOfThreads, CRITICAL_SECTION* critSection) : m_socket(socket), m_listOfThreads(listOfThreads), m_criticalSection(critSection) {}

MyThread::~MyThread() {}

void MyThread::run(void) {
	char* str = new char[255];
	bool exiting = false;
	int iResult;

	do {
		for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
			if (!it->second->isRunning() && it->second->isExited()) {
				//auto temp = it;
				m_listOfThreads->erase(it);
				//delete[] temp->first;
				//delete[] temp->second;
			}
		}

		exiting = false;
		char *OptionBuf = new char[25];

		iResult = recv(m_socket, OptionBuf, 25, 0);
		if (iResult == SOCKET_ERROR || iResult <= 0) {
			exiting = true;
			break;
		}
		OptionBuf[(iResult > 25)? 25 : iResult] = '\0';

		if (!strcmp(OptionBuf, "sendlistofnames")) {
			std::vector<char*> names;
			for (auto person = m_listOfThreads->begin(); person != m_listOfThreads->end(); ++person) {
				names.push_back(person->first);
			}

			for (int i = 0; i < (int)names.size(); ++i) {
				strcpy(str, names[i]);
				iResult = send(m_socket, names[i], strlen(names[i]), 0);
				if (iResult == SOCKET_ERROR || iResult < 0) {
					exiting = true;
					break;
				}
				Sleep(100);
			}

			iResult = send(m_socket, "ack", 3, 0);
			if (iResult == SOCKET_ERROR || iResult < 0) {
				exiting = true;
				break;
			}
		}

		delete[] OptionBuf;
		OptionBuf = nullptr;
	} while (m_socket != SOCKET_ERROR && !exiting);

	printf("%s disconnected.\n", str);
	for (auto it = m_listOfThreads->begin(); it != m_listOfThreads->end(); ++it) {
		if (!strcmp(it->first, str)) {
			//auto temp = it;
			m_listOfThreads->erase(it);
			//delete temp->first;
			//delete temp->second;
			break;
		}
	}
	delete[] str;

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