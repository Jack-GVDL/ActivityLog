#include <iostream>
#include <stdexcept>
#include <stdio.h>
#include <string>
#include <windows.h>


int main() {
	LPSTR 				cmd = "python main_server.py";
    STARTUPINFO 		startup_info;
    PROCESS_INFORMATION process_info;

	ZeroMemory(&startup_info, sizeof(startup_info));
	startup_info.cb = sizeof(startup_info);
	ZeroMemory(&process_info, sizeof(process_info));

	if (!CreateProcess(
		NULL,
		cmd,
		NULL,
		NULL,
		FALSE,
		0,
		NULL,
		NULL,
		&startup_info,
		&process_info
	)) {
		printf("Cannot create the process (%s)", (const char*)cmd);
		return 0;
	};
	
	// message
	printf("Process (%s) created, waiting for exit\n", (const char*)cmd);

	// wait for exit for the process
	WaitForSingleObject(process_info.hProcess, INFINITE);

	CloseHandle(process_info.hProcess);
	CloseHandle(process_info.hThread);

	// message
	printf("Process exited\n");
	while (1);

	return 0;
}