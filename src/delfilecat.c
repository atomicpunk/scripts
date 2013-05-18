#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>

int main(int argc, char* argv[])
{
    long int start = 0;
    long int size = 0;
    char *device = NULL;
    char *buf = NULL;
    FILE *fp = NULL;
    int i;

    if(argc != 4)
    {
        printf("USAGE: device filestart filesize\n");
        return 0;
    }
    device = argv[1];
    if(sscanf(argv[2], "%ld", &start) != 1)
    {
        fprintf(stderr, "Invalid filestart: %s\n", argv[2]);
        return -1;
    }
    if(sscanf(argv[3], "%ld", &size) != 1)
    {
        fprintf(stderr, "Invalid filesize: %s\n", argv[3]);
        return -1;
    }
    if((fp = fopen(device, "rb")) == NULL)
    {
        fprintf(stderr, "Invalid device: %s\n", device);
        return -1;
    }
    if(fseek(fp, start, SEEK_SET) != 0)
    {
        fprintf(stderr, "Failed to reach offset\n", device);
        return -1;
    }
    buf = (char *)calloc(size, sizeof(char));
    if(fread(buf, 1, size, fp) != size)
    {
        fprintf(stderr, "Failed to read total bytes from disk\n");
        return -1;
    }
    printf("%s\n", buf);
    free(buf);
    fclose(fp);
    return 0;
}
