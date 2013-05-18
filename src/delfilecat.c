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
