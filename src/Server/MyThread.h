#pragma once
#include <stdio.h>
#include <WinSock2.h>
#include "SysThread.h"
#ifndef MYTHREAD_H
#define MYTHREAD_H

#include <list>
#include <vector>
#include <Windows.h>

class MyThread : public SysThread {
public:
	MyThread(SOCKET socket, std::list<std::pair<std::pair<char*, std::vector<char*>>, MyThread*>>* listOfThreads, CRITICAL_SECTION* critSection);
	virtual ~MyThread();

protected:
	virtual void run(void);

private:
	SOCKET m_socket;
	std::list<std::pair<std::pair<char*, std::vector<char*>>, MyThread*>>* m_listOfThreads;
	CRITICAL_SECTION* m_criticalSection;
};

#endif /* MYTHREAD_H */