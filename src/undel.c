#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#define BLOCKSIZE (1024*1024)

int main(int argc, char* argv[])
{
    FILE *fp = fopen("/dev/sdb1", "rb");
    unsigned char buf[BLOCKSIZE*2];
    char tgt[1000] = "<title>Brandt Family Archives</title>";
    long int offset = 0;
    int i = 0;

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
