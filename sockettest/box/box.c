#include <stdio.h>
#include <stdlib.h>

#include <netdb.h>
#include <netinet/in.h>

#include <string.h>

#include <pthread.h>
#include <unistd.h>

//first of all, i'd like to make the connection using threads.

void* doProcessing (void *sock);
void* inBound (void *arg);

int main( int argc, char *argv[] ) {
	pthread_t inThread, outThread;
	
	int err=pthread_create(&inThread, NULL, &inBound, NULL);
	if (err != 0)
		printf("Can't create inbound thread.\n", strerror(err));
	
	//dummy process
	while(1){
		sleep(2);
		printf("Dummy.\n");
	}
	
	exit(0);
}

void* inBound(void *arg) {
	int sockfd, portno;
	char buffer[256]; //we won't need this many bytes.
	struct sockaddr_in serv_addr, cli_addr;
	int n, pid;

	/* First call to socket() function */
	sockfd = socket(AF_INET, SOCK_STREAM, 0);

	if (sockfd < 0) {
	  perror("ERROR opening socket");
	  exit(1);
	}

	/* Initialize socket structure */
	bzero((char *) &serv_addr, sizeof(serv_addr));
	portno = 18003;

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = INADDR_ANY;
	serv_addr.sin_port = htons(portno);

	/* Now bind the host address using bind() call.*/
	if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
	  perror("ERROR on binding");
	  exit(1);
	}

	/* Now start listening for the clients, here
	  * process will go in sleep mode and will wait
	  * for the incoming connection
	*/

	listen(sockfd,5); //2nd argument is the max queue length
	int clilen = sizeof(cli_addr);
	   
	pthread_t asdasd;
	
	while (1) {
		int *newsockfd=malloc(sizeof(int));
		*newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);

		//If a connection was accepted, then we'll make another thread which will handle it.
		//A thread will work on the same memory space, so we'll have to allocate for any individual connection.
		
		if (newsockfd < 0) {
			perror("ERROR on accept");
		}
		else{
			int err=pthread_create(&asdasd, NULL, &doProcessing, newsockfd);
			if (err != 0)
				printf("Can't create an inbound processing thread.\n", strerror(err));
			else{

			}
		}
	} //end of while
}

void* doProcessing (void *sock) {
	int n;
	char buffer[256];
	bzero(buffer,256);
	n = read(*((int*)sock),buffer,255);

	if (n < 0) {
		perror("ERROR reading from socket");
		exit(1);
	}

	printf("Here is the message: %s\n",buffer);
	n = write(*((int*)sock),"I got your message",18);

	if (n < 0) {
		perror("ERROR writing to socket");
		exit(1);
	}
	close(*((int*)sock));
	free(sock);
	return(0);
}
