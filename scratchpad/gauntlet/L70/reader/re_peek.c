// re_peek: READ-ONLY batch reader of another process's memory (/proc/PID/mem, O_RDONLY) for reverse-engineering the
// live Clash Royale process. Never writes. Usage (root on the device):
//   re_peek PID < requests.txt > out.txt      each request line: "ADDR LEN" (hex 0x... or decimal), LEN <= 1 MiB
//   output, one line per request: "ADDR LEN <hex bytes>"  or  "ADDR LEN ERR <errno>"
// Build (WSL): gcc -O2 -static -o re_peek re_peek.c
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(int argc, char **argv) {
  if (argc != 2) { fprintf(stderr, "usage: re_peek PID < requests\n"); return 2; }
  char path[64]; snprintf(path, sizeof path, "/proc/%s/mem", argv[1]);
  int fd = open(path, O_RDONLY);
  if (fd < 0) { perror("open"); return 1; }
  static unsigned char buf[1 << 20];
  char line[256];
  while (fgets(line, sizeof line, stdin)) {
    uint64_t addr; unsigned long len;
    if (sscanf(line, "%" SCNi64 " %li", &addr, &len) != 2 || len == 0 || len > sizeof buf) continue;
    ssize_t n = pread(fd, buf, len, (off_t)addr);
    if (n != (ssize_t)len) { printf("0x%" PRIx64 " %lu ERR %d\n", addr, len, errno); continue; }
    printf("0x%" PRIx64 " %lu ", addr, len);
    for (unsigned long i = 0; i < len; i++) printf("%02x", buf[i]);
    putchar('\n');
  }
  close(fd);
  return 0;
}
