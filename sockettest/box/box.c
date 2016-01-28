#include <stdio.h>
#include <stdlib.h>

#include <netdb.h>
#include <netinet/in.h>

#include <string.h>

#include <pthread.h>
#include <unistd.h>
#include <ctype.h>

//first of all, i'd like to make the connection using threads.

void* doProcessingDev (void *sock);
void* fromDevice (void *port);
void* fromServer (void *port);
char isNumber(char* str);
int initSocketListener(int port, void* (*processFunc)(void* arg));

pthread_attr_t attr;

int main(int argc, char *argv[] ) {
	
	//checking if we got 1 argument, and if that's a number.
	if(!(argc==2 && isNumber(argv[1]))){
		printf("Usage: %s [portno]\n", argv[0]);
		return(1);
	}
	
	//converting given port arg to integers, so we can pass their pointers to threads later.
	int port = strtol(argv[1], (char**)NULL, 10);
	int toDevPort=port;
	int fromDevPort=port+1;
	int toSrvPort=port+2;
	int fromSrvPort=port+3;
	
	//the two main listener thread.
	pthread_t fromDevThr, fromSrvThr;
	
	//initializing pthread attributes as all threads will be created detached
	pthread_attr_init(&attr);
	pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
	
	//creating the thread that will serve the incoming connections from the local devices.
	int err;
	err=pthread_create(&fromDevThr, &attr, &fromDevice, &fromDevPort);
	if (err != 0)
		perror("\nERROR - Can't create fromDevThr thread.");
		
	//creating the thread that will serve the incoming connections from the main server.
	//err=pthread_create(&fromSrvThr, &attr, &fromServer, &fromSrvPort);
	//if (err != 0)
	//	perror("\nERROR - Can't create fromSrvThr thread.");
		
	
	pthread_join(fromDevThr, NULL);
	pthread_exit(NULL);
}

int initSocketListener(int port, void * (*processFunc)(void* arg)){
	int sockfd;
	struct sockaddr_in serv_addr, cli_addr;
	int n, pid;

	/* First call to socket() function */
	sockfd = socket(AF_INET, SOCK_STREAM, 0);

	if (sockfd < 0) {
	  perror("\nERROR - Couldn't open socket.");
	  return(1);
	}

	/* Initialize socket structure */
	bzero((char *) &serv_addr, sizeof(serv_addr));

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = INADDR_ANY;
	serv_addr.sin_port = htons(port);

	/* Now bind the host address using bind() call.*/
	if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
	  perror("\nERROR - Couldn't bind.");
	  return(2);
	}

	/* Now start listening for the clients, here
	  * process will go in sleep mode and will wait
	  * for the incoming connection
	*/

	listen(sockfd,5); //2nd argument is the max queue length
	int clilen = sizeof(cli_addr);
	
	while (1) {
		int *newsockfd=malloc(sizeof(int));
		*newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);

		//If a connection was accepted, then we'll make another thread which will handle it.
		//A thread will work on the same memory space, so we'll have to allocate for any individual connection.
		
		if (newsockfd < 0) {
			perror("\nERROR - Error on accept");
			return(3);
		}
		else{
			pthread_t *thr =malloc(sizeof(pthread_t));
			int err=pthread_create(thr, &attr, processFunc, newsockfd);
			free(thr);
			if (err != 0){
				perror("\nERROR - Couldn't create an fromDevice processing thread.");
				return(4);
			}
		}
	} //end of while
	return(0);
}

void* fromDevice(void *port) {
	initSocketListener(*(int*)port, &doProcessingDev);
	pthread_exit(NULL);
}

void* fromServer(void *port){
	//basically here we'll just wait for the server to say something?
	//or are we always the first to say hello? yes that would be better?
	//but what about when an other box is triggering something here?
	//yes we do need this
	
}

void* doProcessingDev (void *sock) {
	int n;
	char buffer[16];
	bzero(buffer,16);
	n = read(*((int*)sock),buffer,16);

	if (n < 0) {
		perror("\nERROR - Couldn't read from socket.");
		pthread_exit(NULL);
	}

	//Here we can manipulate what we have just read.
	for(int i=0; i<16;i++){
		unsigned char nthByte=(unsigned char) *(buffer+i);
		printf("Here is the %d. byte: %d\n", i, nthByte);
	}
	//

	close(*((int*)sock));
	free(sock);
	pthread_exit(NULL);
}

char isNumber(char* str){
	int i=0;
	while(str[i]!='\0'){
		if(!isdigit(str[i])){
			return(0);
		}
		i++;
	}
	return(1);
}
