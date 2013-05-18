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
    char **tgt = NULL;
    long int offset = 0;
    int i, j, tgtcnt = 0;

    if(argc < 4)
    {
        printf("USAGE: device offset searchstr1 searchstr2 ...\n");
        return 0;
    }
    device = argv[1];
    if(sscanf(argv[2], "%ld", &offset) != 1)
    {
        fprintf(stderr, "Invalid filestart: %s\n", argv[2]);
        return -1;
    }

    tgtcnt = argc - 3;
    tgt = (char **)calloc(tgtcnt, sizeof(char *));
    for(i = 0; i < tgtcnt; i++)
        tgt[i] = argv[i+3];

    if((fp = fopen(device, "rb")) == NULL)
    {
        fprintf(stderr, "Invalid device: %s\n", device);
        return -1;
    }
    if(fseek(fp, offset, SEEK_SET) != 0)
    {
        fprintf(stderr, "Failed to reach offset\n", device);
        return -1;
    }

    printf("Searching %s for:\n", device);
    for(i = 0; i < tgtcnt; i++)
        printf("    \"%s\"\n", tgt[i]);
    printf("\n");

    fread(buf, 1, BLOCKSIZE, fp);
    while(fread(&buf[BLOCKSIZE], 1, BLOCKSIZE, fp) > 0)
    {
        for(i = 0; i < BLOCKSIZE; i++)
        {
            char *s = &buf[i];
            for(j = 0; j < tgtcnt; j++)
            {
                if(strncmp(s, tgt[j], strlen(tgt[j])) == 0)
                {
                    printf("%12ld: \"%s\"\n", offset+i, tgt[j]);
                }
            }
        }
        memmove(buf, &buf[BLOCKSIZE], BLOCKSIZE);
        offset += BLOCKSIZE;
    }

    fclose(fp);
    return 0;
}
