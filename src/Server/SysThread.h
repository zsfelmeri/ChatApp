#pragma once
#include <limits.h>
#include <Windows.h>

class SysThread {
public:
	SysThread(void);
	virtual ~SysThread();
	virtual bool start(void);
	virtual bool stop(unsigned int timeout = 0);
	inline volatile bool& isRunning(void) {
		return m_bRunning;
	}
	inline volatile bool& isExited(void) {
		return m_bExited;
	}

	static const unsigned int INFINITE_WAIT;

protected:
	virtual void run(void);

private:
	friend DWORD WINAPI runStub(LPVOID mthred);

	volatile bool m_bRunning;
	volatile bool m_bExited;
	HANDLE m_thread;
};