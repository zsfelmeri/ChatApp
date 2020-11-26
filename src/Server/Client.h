#pragma once
#include "MyThread.h"

struct Client {
	MyThread* client;
	char* name = new char[255];

	Client(MyThread* _client, char* _name) : client(_client), name(_name) {}
};