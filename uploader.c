#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>

int upload(char conts[7], char *filename[], long int filesize) {
	/* Reading token file */
	FILE *fptrtoken;
	fptrtoken = fopen(".token", "r");
	if (fptrtoken == NULL) {
		fprintf(stderr, "Please make a file named .token and put your upload token in it!\n");
		return 1;
	}
	char token[33];
	fgets(token, 33, fptrtoken);
	fclose(fptrtoken);

	/* Authorization header */
	char authorization[49];
	strcpy(authorization, "Authorization: ");
	strcat(authorization, token);

	/* HTTP headers */
	struct curl_slist *headers=NULL;
	headers = curl_slist_append(headers, authorization);
	headers = curl_slist_append(headers, "User-Agent: ratted-systems-uploader (C Edition)");
	headers = curl_slist_append(headers, "Expect:");

	/* Initializing libcURL handle */
	CURL *up = curl_easy_init();
	
	/* Creating MIME handle */
	curl_mime *form = curl_mime_init(up);
	curl_mimepart *field = NULL;

	if (!up) {
		return 1;
	}

	/* Setting cURL handle options */
	curl_easy_setopt(up, CURLOPT_POST, 1L);
	curl_easy_setopt(up, CURLOPT_POSTFIELDS, conts);
	curl_easy_setopt(up, CURLOPT_POSTFIELDSIZE, filesize);
	curl_easy_setopt(up, CURLOPT_HTTPHEADER, headers);

	/* Making form or something */
	field = curl_mime_addpart(form);
	curl_mime_name(field, "file");
	curl_mime_filedata(field, *filename);

	CURLcode res;
	
	/* Setting more handle options
	 * (POST request form and URL) */
	curl_easy_setopt(up, CURLOPT_MIMEPOST, form);
	curl_easy_setopt(up, CURLOPT_URL, "https://ratted.systems/upload/new");
	
	/* Doing the thing */
	res = curl_easy_perform(up);
	
	/* Cleanup */
	curl_easy_cleanup(up);
	curl_mime_free(form);
    	curl_slist_free_all(headers);

	return res;

}

int main(int argc, char *argv[]) {
	/* Initializing file pointer and opening specified file */
	FILE *fptr;
	fptr = fopen(argv[1], "rb");
	if (fptr == NULL) {
		fprintf(stderr, "File not found, please specify a file that exists!\n");
		return 1;
	}
	
	/* Checking file size and storing it in a variable */
	fseek(fptr, 0L, SEEK_END);
	long int filesize = ftell(fptr);
	
	/* Allocating memory and storing file */
	char* buffer = malloc(filesize);
	fread(buffer, filesize, 1, fptr);

	/* Calling upload function, freeing memory and closing file */
	upload(buffer, &argv[1], filesize);
	free(buffer);
	fclose(fptr);
}
