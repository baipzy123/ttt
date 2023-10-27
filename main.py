import base64
import hashlib
import json
import random
import time
from urllib import parse
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes
from Cryptodome.Random import random
from Cryptodome.Cipher import PKCS1_OAEP, AES
from Cryptodome.Hash import CMAC, SHA256, HMAC, SHA1
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pss
from Cryptodome.Util import Padding
from google.protobuf.message import DecodeError
from google.protobuf import text_format
import logging
import yaml
from tabulate import tabulate
from wasmer_compiler_cranelift import Compiler
from wasmer import Store, Type, Function, Memory, Module, ImportObject, engine, Instance, Table
from pywidevine.L3.cdm import deviceconfig
from pywidevine.L3.decrypt.wvdecryptcustom import WvDecrypt
import re, requests, time, json
from hashlib import md5
import base64
from tools import rsa_dec, aes_decrypt, djb2Hash, b64decode, sha1withrsa, check_file, get_config
from tx import TX
from iqy import iqy
from yk import YouKu

if __name__ == '__main__':
    check_file()
    config = get_config()
    txck = config["txck"]
    yk = config["yk"]
    aqy = config["aqy"]
    tx = TX(txck)
    iq = iqy(aqy)
    youku = YouKu(yk)
    while True:
            url = input("请输入视频链接：")
            if "v.qq.com" in url:
                tx.run(url)
            elif "iqiyi.com" in url:
                iq.run(url)
            elif "youku.com" in url:
                youku.start(url)
            else:
                print("暂不支持该链接")

