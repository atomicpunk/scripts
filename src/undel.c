/*
 *  Copyright 2012 Todd Brandt <tebrandt@frontier.com>
 *
 *  This program is free software; you may redistribute it and/or modify it
 *  under the same terms as Perl itself.
 *     trancearoundtheworld mp3 archive sync utility
 *     Copyright (C) 2012 Todd Brandt <tebrandt@frontier.com>
 *
 *     This program is free software; you can redistribute it and/or modify
 *     it under the terms of the GNU General Public License as published by
 *     the Free Software Foundation; either version 2 of the License, or
 *     (at your option) any later version.
 *
 *     This program is distributed in the hope that it will be useful,
 *     but WITHOUT ANY WARRANTY; without even the implied warranty of
 *     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *     GNU General Public License for more details.
 *
 *     You should have received a copy of the GNU General Public License along
 *     with this program; if not, write to the Free Software Foundation, Inc.,
 *     51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */

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
    char synopsis[101];
    char **tgt = NULL;
    long int offset = 0;
    int i, j, tgtcnt = 0;

    memset(synopsis, 0, 101);
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

    printf("Searching %s at offset %ld for:\n", device, offset);
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
                    printf("FOUND AT %12ld: \"%s\"\n\n", offset+i, tgt[j]);
                    memcpy(synopsis, s, 100);
                    printf("%s\n\n", synopsis);
                }
            }
        }
        memmove(buf, &buf[BLOCKSIZE], BLOCKSIZE);
        offset += BLOCKSIZE;
    }

    fclose(fp);
    return 0;
}
