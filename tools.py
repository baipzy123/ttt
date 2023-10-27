import base64
import hashlib
import os
import yaml
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Util.Padding import pad, unpad

yaml_path = "./config.yaml"


def get_pssh(inia):
    raw = base64.b64decode(inia) if isinstance(inia, str) else inia
    offset = raw.rfind(b'pssh')
    d = base64.b64encode(raw[offset - 4:offset - 4 + raw[offset - 1]])
    return d.decode('utf-8')


def is_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def check_file():
    files = ["./chache", "./download"]
    for file in files:
        is_dir(file)


def write_yaml(r):
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(r, f)


def read_yaml():
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def updata_yaml(k, v):
    old_data = read_yaml()
    old_data[k] = v
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(old_data, f)


def get_config():
    try:
        data = read_yaml()
    except FileNotFoundError:
        tx = input("请输入腾讯ck：")
        yk = input("请输入优酷ck：")
        aqy = input("请输入爱奇艺ck：")
        data = {
            "txck": tx,
            "yk": yk,
            "aqy": aqy,
        }
        write_yaml(data)
    return data


def b64decode(data: str):
    data = data + "=" * (4 - len(data) % 4)
    return base64.b64decode(data)


def djb2Hash(e):
    t = 5381
    for r in range(len(e)):
        t += (t << 5) + ord(e[r])
    return t & 2147483647


def aes_encrypt(key: bytes, data: bytes, iv: bytes = None):
    if iv is None:
        iv = b'\x00' * 16
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data = pad(data, cipher.block_size)
    return cipher.encrypt(data)


def aes_decrypt(key: bytes, data: bytes, iv: bytes = None):
    if iv is None:
        iv = b'\x00' * 16
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data = cipher.decrypt(data)
    return unpad(data, cipher.block_size)


def rsa_dec(prikey, data: bytes):
    key = RSA.importKey(prikey)
    cipher = PKCS1_OAEP.new(key)
    ret = b""
    k = cipher._key.size_in_bytes()
    for i in range(0, len(data), k):
        ret += cipher.decrypt(data[i:i + k])
    return ret.decode()


def sha1withrsa(prikey, data: bytes):
    key = RSA.importKey(prikey)
    h = SHA1.new(data)
    signer = pkcs1_15.new(key)
    signature = signer.sign(h)
    return base64.b64encode(signature).decode()


def dealck(ck: str) -> dict:
    ck = ck.split(";")
    ckdict = {}
    for i in ck:
        i = i.strip()
        i = i.split("=")
        ckdict[i[0]] = i[1]
    return ckdict


def md5(data: str) -> str:
    return hashlib.md5(data.encode()).hexdigest()


def get_size(a):
    size_suffixes = ['B', 'KB', 'MB', 'GB']
    for suffix in size_suffixes:
        if a < 1024:
            return f"{a:.2f}{suffix}"
        a /= 1024
    return f"{a:.2f}TB"
