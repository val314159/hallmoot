.PHONY: run clean

CC = gcc
CFLAGS = -Wall -g

hello: hello.c
	$(CC) $(CFLAGS) -o hello hello.c

run: hello
	./hello

clean:
	rm -f hello
