# PFishHook
PFishHook is an x64 inline hook library. It is developed and tested on Linux, but "should" be working on POSIX-compatible systems, like UNIX and macOS. The support for Windows is planned to be developed.

PFishHook can help you intercept calls to a function, and replace the the target function with yours. It is useful to hook APIs to monitor and change the behavior of them.

## Build instructions
PFishHook depends on Zydis, a Fast and lightweight x86/x86-64 disassembler library. First, you need to build Zydis.

```shell
git submodule init
git submodule update
mkdir build
cd build
cmake ..
make
```
Now, you can find libPFishHook.a in "build" directory. To compile with PFishHook, you should add build/libPFishHook.a and build/3rdparty/zydis/libZydis.a to your link arguments.

## How to use

The most important API is

```C++
HookStatus HookIt(void* oldfunc, void** poutold, void* newfunc);

```
The parameter "oldfunc" is the target function to hook. "poutold" is the pointer to the pointer to the "shadown function", and "newfunc" is your function to replace the "oldfunc".
In your "newfunc", you can call the "shadown" function to call the unmodified version of function.


```C++
typedef ssize_t(*ptrread)(int fd, void *buf, size_t nbytes);
ptrread oldread;
extern "C" ssize_t myread(int fd, void *buf, size_t nbytes)
{
	fprintf(stderr, "read\n");
	ssize_t ret= oldread(fd,buf,nbytes);
	fprintf(stderr, "read ret%d\n",ret);
	return ret;
}

void readwrite()
{
	int fd, size;
	char s[] = "Linux Programmer!\n", buffer[80];
	fd = open("/tmp/temp", O_WRONLY | O_CREAT);
	write(fd, s, sizeof(s));
	close(fd);
	fd = open("/tmp/temp", O_RDONLY);
	size = read(fd, buffer, sizeof(buffer));
	close(fd);
	printf("%s", buffer);
}
int main()
{
  void* read= dlsym(RTLD_NEXT, "read"));
	printf("Hook %d\n",HookIt(read, (void**)&oldread, (void*)myread));
	readwrite();
	return 0;
}
```

## How it works
PFishHook copies a few bytes at the head of the target function to a new "shadown function". Then it replace the head of the target function with a jump to the function specified by the user. And it returns the address of the "shadown function" to users.

The "shadown function" has the same functionality of the original function.

## Limitations and known issues
 * PFishHook can only deal with functions with length at least 14 bytes (which is the size of "jump" instructions).
 * Some Linux syscall wrapper functions like "read" has RIP-relative instructions in the function's head. We move the function's head to the shadow function, so the RIP has change. In this case, we need to patch RIP-relative instructions' displacement.
 * PFishHook do not allow any jumps into the middle of replaced (hooked) funcion head.

Users should check the functions to hook carefully to see whether the function violates the above limitations.
