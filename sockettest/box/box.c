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
char isNumber(char* str);

pthread_attr_t attr;

int main(int argc, char *argv[] ) {
	//let's check if the 1st argument is a number
	if(!(argc==2 && isNumber(argv[1]))){
		printf("Usage: %s [portno]\n", argv[0]);
		return(1);
	}
	int port = strtol(argv[1], (char**)NULL, 10);
	
	int toDevPort=port;
	int fromDevPort=port+1;
	int toSrvPort=port+2;
	int fromSrvPort=port+3;
	
	pthread_t fromDevThr, fromSrvThr;
	
	//initializing pthread attributes as all threads wil be created detached
	pthread_attr_init(&attr);
	pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
	
	int err=pthread_create(&fromDevThr, &attr, &fromDevice, &fromDevPort);
	if (err != 0)
		perror("\nERROR - Can't create fromDevice thread.");
	
	pthread_join(fromDevThr, NULL);
	pthread_exit(NULL);
}

void* fromDevice(void *port) {
	int sockfd;
	//char buffer[16]; //we won't need this many bytes.
	struct sockaddr_in serv_addr, cli_addr;
	int n, pid;

	/* First call to socket() function */
	sockfd = socket(AF_INET, SOCK_STREAM, 0);

	if (sockfd < 0) {
	  perror("\nERROR - Couldn't open socket.");
	  pthread_exit(NULL);
	}

	/* Initialize socket structure */
	bzero((char *) &serv_addr, sizeof(serv_addr));

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = INADDR_ANY;
	serv_addr.sin_port = htons(*((int*)port));

	/* Now bind the host address using bind() call.*/
	if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
	  perror("\nERROR - Couldn't bind.");
	  pthread_exit(NULL);
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
		}
		else{
			pthread_t *thr =malloc(sizeof(pthread_t));
			int err=pthread_create(thr, &attr, &doProcessingDev, newsockfd);
			free(thr);
			if (err != 0)
				perror("\nERROR - Couldn't create an fromDevice processing thread.");
			else{

			}
		}
	} //end of while
	pthread_exit(NULL);
}

void* fromServer(void *arg){
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
