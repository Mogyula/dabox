/*
 * main.c
 *
 *  Created on: 2016. ápr. 30.
 *      Author: mogyula
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/file.h>

int isOnlyInstance();

int main(){
 printf("%d\n", isOnlyInstance());
 fflush(stdout);
 sleep(10);
 return 0;
}

//we are going to check, if this is the only instance running.
int isOnlyInstance(){
	struct flock fl;
	char *lockFile = "/tmp/.daboxsrv.lck";
	int fd = fileno(fopen(lockFile, "r")); //it must be available for reading
	
	if(fd == -1){
		printf("Could not open /tmp/.daboxsrv.lck for reading.");
		return -1;
	}
	
	if (fcntl(fd, F_GETLK, &fl) == -1){
		printf("Could not read lock state of /tmp/.daboxsrv.lck");
		return -1;
	}
	
	if(fl.l_type != F_UNLCK){ //is there a lock on it?
		return 0; //yes, there is.
	}else{	
		fl.l_type   = F_RDLCK;
		fl.l_whence = SEEK_SET;
		fl.l_start  = 0;
		fl.l_len    = 0;
		fl.l_pid    = getpid();
		
		if(fcntl(fd, F_SETLK, &fl) == -1){
			printf("Could not set read lock on /tmp/.daboxsrv.lck");
			return 1; //just in case
		}
		
		return 1;
	}
	return -1;
}
