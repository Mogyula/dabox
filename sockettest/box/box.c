#include <stdio.h>
#include <stdlib.h>

#include <netdb.h>
#include <netinet/in.h>

#include <string.h>

#include <pthread.h>

//first of all, i'd like to make the connection using threads.

void doprocessing (int sock);
void doSome ();

int main( int argc, char *argv[] ) {
   int sockfd, portno;
   char buffer[256];
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
   portno = 18002;
   
   serv_addr.sin_family = AF_INET;
   serv_addr.sin_addr.s_addr = INADDR_ANY;
   serv_addr.sin_port = htons(portno);
   
   /* Now bind the host address using bind() call.*/
   if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
      perror("ERROR on binding");
      exit(1);
   }
   
   //it's "above" processes until this point.
   
   /* Now start listening for the clients, here
      * process will go in sleep mode and will wait
      * for the incoming connection
   */
   
   listen(sockfd,5); //2nd argument is the max queue length
   
   doSome(sockfd, cli_addr);
}

void doprocessing (int sock) {
   int n;
   char buffer[256];
   bzero(buffer,256);
   n = read(sock,buffer,255);
   
   if (n < 0) {
      perror("ERROR reading from socket");
      exit(1);
   }
   
   printf("Here is the message: %s\n",buffer);
   n = write(sock,"I got your message",18);
   
   if (n < 0) {
      perror("ERROR writing to socket");
      exit(1);
   }
	
}

void doSome(int sockfd, struct sockaddr_in cli_addr){
	int clilen = sizeof(cli_addr);
	//this is just a test to try threading.
	while (1) {
		int newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
		
		if (newsockfd < 0) {
		 perror("ERROR on accept");
		 exit(1);
		}

		doprocessing(newsockfd);
		close(newsockfd);

   }
}
