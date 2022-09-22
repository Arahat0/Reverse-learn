def init(sbox,key,len):
    t=[0]*256
    for i in range(256):
        t[i] = key[i%len]
    j = 0
    for i in range(256):
        j = (j+sbox[i]+t[i])%256
        sbox[i], sbox[j] = sbox[j], sbox[i]

def crypt(sbox,len):
    j=0
    for i in range(len):
        i=(i+1)%256
        j=(j+sbox[i])%256
        sbox[i], sbox[j] = sbox[j], sbox[i]
        t=(sbox[i]+sbox[j])%256
        key.append(sbox[t])

date0 = list(input("输入明文："))
key0 = list(input("输入密钥："))
klen = len(key0)
key=list()
for i in key0:
    key.append(ord(i))
sbox = [i for i in range(256)]
dlen = len(date0)
date=list()
for i in date0:
    date.append(ord(i))

init(sbox,key,klen)
key=[]
crypt(sbox,dlen)
print(key)
for i in range(len(date)):
    date[i]^=key[i]
date=''.join(map(chr,date))
print("加密后的数据：",date)