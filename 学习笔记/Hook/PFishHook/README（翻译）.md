# PFishHook
PFishHook是一个x64内联挂钩库。它是在Linux上开发和测试的，但“应该”在POSIX兼容系统上工作，如UNIX和macOS。计划开发对Windows的支持。

PFishHook可以帮助您拦截对函数的调用，并用您的函数替换目标函数。挂钩API以监视和更改它们的行为非常有用。

## Build instructions
PFishHook依赖于Zydis，这是一个快速、轻量级的x86/x86-64反汇编程序库。首先，您需要构建Zydis。

```shell
git submodule init
git submodule update
mkdir build
cd build
cmake ..
make
```
现在，您可以找到libPFishHook.a在“build”目录中。要使用PFishHook进行编译，应该添加build/libPFishHook.a和build/3rdparty/zydis/libZydis.a添加到链接参数。

## How to use

最重要的API是

```C++
HookStatus HookIt(void* oldfunc, void** poutold, void* newfunc);

```
参数“oldfunc”是要挂钩的目标函数。“poutold”是指向“shadown函数”指针的指针，“newfunc”是替换“oldfunc”的函数。
在“newfunc”中，可以调用“shadown”函数来调用未修改版本的函数。


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
PFishHook将目标函数开头的几个字节复制到一个新的“shadown函数”。然后，它用跳转到用户指定的函数来替换目标函数的头部。并将“shadown函数”的地址返回给用户。
“shadown函数”具有与原始函数相同的功能。

## Limitations and known issues
 * PFishHook只能处理长度至少为14字节（即“跳转”指令的大小）的函数。

 * 一些Linux系统调用包装器函数（如“read”）在函数的头部有RIP相关指令。我们将函数的头部移动到shadow函数，因此RIP发生了变化。在这种情况下，我们需要修补RIP相关指令的位移。

 * PFishHook不允许任何跳转到替换（钩）函数头的中间。

   用户应该仔细检查要挂钩的函数，看看该函数是否违反了上述限制。
