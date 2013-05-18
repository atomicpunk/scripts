#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#define BLOCKSIZE (1024*1024)

int main(int argc, char* argv[])
{
    FILE *fp = NULL;
    char *device = NULL;
    unsigned char buf[BLOCKSIZE*2];
    char *tgt = NULL;
    long int offset = 0;
    int i = 0;

    if(argc != 3)
    {
        printf("USAGE: device searchstring\n");
        return 0;
    }
    device = argv[1];
    tgt = argv[2];

    if((fp = fopen(device, "rb")) == NULL)
    {
        fprintf(stderr, "Invalid device: %s\n", device);
        return -1;
    }

    printf("Searching %s for [%s]...\n", device, tgt);

    fread(buf, 1, BLOCKSIZE, fp);
    while(fread(&buf[BLOCKSIZE], 1, BLOCKSIZE, fp))
    {
        for(i = 0; i < BLOCKSIZE; i++)
        {
            char *s = &buf[i];
            if(strncmp(s, tgt, strlen(tgt)) == 0)
            {
                printf("FOUND %s at %ld\n", tgt, offset+i);
            }
        }
        memmove(buf, &buf[BLOCKSIZE], BLOCKSIZE);
        offset += BLOCKSIZE;
    }
    fclose(fp);
    return 0;
}
