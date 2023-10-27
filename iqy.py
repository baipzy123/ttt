import base64
import json
import time
from urllib import parse
import requests
from tabulate import tabulate
from pywidevineb.L3.cdm import deviceconfig
from pywidevineb.L3.decrypt.wvdecryptcustom import WvDecrypt
from tools import dealck, md5, get_size, get_pssh


def get_key(pssh):
    LicenseUrl = "https://drml.video.iqiyi.com/drm/widevine?ve=0"
    wvdecrypt = WvDecrypt(init_data_b64=pssh, device=deviceconfig.device_android_generic)
    widevine_license = requests.post(url=LicenseUrl, data=wvdecrypt.get_challenge())
    license_b64 = base64.b64encode(widevine_license.content)
    wvdecrypt.update_license(license_b64)
    correct, keys = wvdecrypt.start_process()
    for key in keys:
        print('--key ' + key)
    key_string = ' '.join([f"--key {key}" for key in keys])
    return key_string


class iqy:
    def __init__(self, aqy):
        self.ck = aqy
        ckjson = dealck(aqy)
        self.P00003 = ckjson.get('P00003', "1008611")
        self.pck = ckjson.get('P00001')
        self.dfp = ckjson.get('__dfp', "").split("@")[0]
        self.QC005 = ckjson.get('QC005', "")
        self.requests = requests.Session()

        self.requests.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": self.ck,
        })
        self.bop = f"{{\"version\":\"10.0\",\"dfp\":\"{self.dfp}\",\"b_ft1\":8}}"

    @staticmethod
    def parse(shareurl):
        try:
            url = "https://iface2.iqiyi.com/video/3.0/v_play"
            params = {
                "app_k": "20168006319fc9e201facfbd7c2278b7",
                "app_v": "8.9.5",
                "platform_id": "10",
                "dev_os": "8.0.1",
                "dev_ua": "Android",
                "net_sts": "1",
                "secure_p": "GPhone",
                "secure_v": "1",
                "dev_hw": "{\"cpu\":0,\"gpu\":\"\",\"mem\":\"\"}",
                "app_t": "0",
                "h5_url": shareurl
            }
            response = requests.get(url, params=params)
            data = response.json()
            pid = data['play_pid']
            aid = data['play_aid']
            tvid = data['play_tvid']
            Album = data['album']
            Title = Album['_t']
            Cid = Album['_cid']
            return pid, aid, tvid, Title, Cid
        except Exception as e:
            print(e)
            return None, None, None, None, None

    @staticmethod
    def get_avlistinfo(title, albumId, cid, pid):
        rets = []
        page = 1
        size = 200

        def getlist6():
            url = "https://pcw-api.iqiyi.com/album/source/svlistinfo"
            params = {
                "cid": "6",
                "sourceid": pid,
                "timelist": ",".join([str(i) for i in range(2000, 2026)]),
            }
            response = requests.get(url, params=params)
            data = response.json()['data']
            for a, b in data.items():
                for i in b:
                    ret = {
                        "album": title,
                        "name": i['name'],
                        "tvId": i['tvId'],
                    }
                    rets.append(ret)

        def getlist():
            aid = albumId
            url = "https://pcw-api.iqiyi.com/albums/album/avlistinfo"
            params = {
                "aid": aid,
                "page": page,
                "size": size
            }
            response = requests.get(url, params=params).json()
            if response['code'] != 'A00000':
                return None
            data = response['data']
            total = data['total']
            if total > size:
                for i in range(2, total // size + 2):
                    params['page'] = i
                    response = requests.get(url, params=params).json()
                    data['epsodelist'].extend(response['data']['epsodelist'])
            for i in data['epsodelist']:
                ret = {
                    "album": title,
                    "name": i['name'],
                    "tvId": i['tvId'],
                }
                rets.append(ret)

        if cid == 1:
            ret = {
                "album": title,
                "name": title,
                "tvId": albumId,
            }
            rets.append(ret)
        elif cid == 6:
            getlist6()
        else:
            getlist()
        return rets

    def get_param(self, tvid="", vid=""):
        tm = str(int(time.time() * 1000))
        authKey = md5("d41d8cd98f00b204e9800998ecf8427e" + tm + str(tvid))
        params = {
            "tvid": tvid,
            "bid": "600",
            "vid": "",
            "src": "01010031010000000000",
            "vt": "0",
            "rs": "1",
            "uid": self.P00003,
            "ori": "pcw",
            "ps": "0",
            "k_uid": "dc7c8156286e94182d2843ada4ef6050",
            "pt": "0",
            "d": "0",
            "s": "",
            "lid": "0",
            "cf": "0",
            "ct": "0",
            "authKey": authKey,
            "k_tag": "1",
            "dfp": self.dfp,
            "locale": "zh_cn",
            "pck": self.pck,
            "k_err_retries": "0",
            "up": "",
            "sr": "1",
            "qd_v": "5",
            "tm": tm,
            "qdy": "u",
            "qds": "0",
            "ppt": "0",
            "k_ft1": "706436220846084",
            "k_ft4": "1162321298202628",
            "k_ft2": "262335",
            "k_ft5": "134217729",
            "k_ft6": "128",
            "k_ft7": "688390148",
            "fr_300": "120_120_120_120_120_120",
            "fr_500": "120_120_120_120_120_120",
            "fr_600": "120_120_120_120_120_120",
            "fr_800": "120_120_120_120_120_120",
            "fr_1020": "120_120_120_120_120_120",
        }
        dash = f'/dash?'
        for a, b in params.items():
            dash += f"{a}={b}&"
        dash = dash[:-1] + "&bop=" + parse.quote(self.bop) + "&ut=14"
        vf = md5(dash + "tle8orw4vetejc62int3uewiniecr18i")
        dash += f"&vf={vf}"
        return dash

    def get_dash(self, tvid="", vid=""):
        params = self.get_param(tvid=tvid, vid=vid)
        url = "https://cache.video.iqiyi.com" + params
        res = self.requests.get(url)
        return res.json()

    def run(self, url=None):
        url = input("请输入爱奇艺分享链接：") if url is None else url
        pid, aid, tvid, title, cid = self.parse(url)
        if pid is None:
            print("解析失败")
            return
        avlist = self.get_avlistinfo(title, aid, cid, pid)
        if avlist is None:
            print("获取列表失败")
            return
        table = tabulate(avlist, headers="keys", tablefmt="grid", showindex=range(1, len(avlist) + 1))
        print(table)
        index = input("请输入序号：")
        index = index.split(",")
        for i in index:
            if i.isdigit():
                i = int(i)
                if i > len(avlist):
                    print("序号错误")
                    continue
                tvId = avlist[i - 1]['tvId']
                name = avlist[i - 1]['name']
                ctitle = avlist[i - 1]['album']
                print(f"正在获取{ctitle} {name}的m3u8")
                response = self.get_dash(tvid=tvId)
                try:
                    if response['data']['boss_ts']['code'] != 'A00000':
                        print(f'获取m3u8失败\n')
                        print(response['data']['boss_ts']['msg'])
                        continue
                except:
                    pass
                data = response['data']
                program = data['program']
                if 'video' not in program:
                    print("无视频")
                    continue
                video = program['video']
                audio = program['audio']
                stl = program.get("stl", [])
                '''
                                list = []
                for a in video:
                    scrsz = a.get('scrsz', '')
                    size = a['vsize']
                    vid = a['vid']
                    list.append((scrsz, vid, size))
                list.sort(key=lambda x: x[-1], reverse=True)
                tb = tabulate(list, headers=["分辨率", "vid", "大小"], tablefmt="grid",
                              showindex=range(1, len(list) + 1))
                print(tb)
                index = input("请输入序号：")
                index = index.split(",")
                for i in index:
                    vid = list[int(i) - 1][1]
                    response = self.get_dash(tvid=tvId, vid=vid)
                    try:
                        if response['data']['boss_ts']['code'] != 'A00000':
                            print(f'获取m3u8失败\n')
                            print(response['data']['boss_ts']['msg'])
                            continue
                    except:
                        pass
                    data = response['data']
                    program = data['program']
                    if 'video' not in program:
                        print("无视频")
                        continue
                    video = program['video']
                '''
                for a in video:
                    try:
                        scrsz = a.get('scrsz', '')
                        vsize = get_size(a['vsize'])
                        m3u8data = a['m3u8']
                        fr = str(a['fr'])
                        name = name + "_" + scrsz + "_" + vsize + "_" + fr + 'fps'
                        name = name.replace(' ', '_')
                        file = f"./chache/{name}.m3u8"
                        savepath = f"./download/iqy/{ctitle}"
                        with open(file, 'w') as f:
                            f.write(m3u8data)
                        if m3u8data.startswith('{"payload"'):
                            m3u8data = json.loads(m3u8data)
                            init = m3u8data['payload']['wm_a']['audio_track1']['codec_init']
                            pssh = get_pssh(init)
                            key_string = get_key(pssh)
                            cmd = f"N_m3u8DL-RE.exe \"{file} \" --tmp-dir ./cache --save-name \"{name}\" --save-dir \"{savepath}\" --thread-count 16 --download-retry-count 30 --auto-select --check-segments-count " + key_string + " --decryption-binary-path ./mp4decrypt.exe  -M format=mp4"
                        else:
                            cmd = f"N_m3u8DL-RE.exe \"{file} \" --tmp-dir ./cache --save-name \"{name}\" --save-dir \"{savepath}\" --thread-count 16 --download-retry-count 30 --auto-select --check-segments-count "
                        with open(f"{ctitle}.bat", 'a', encoding='gbk') as f:
                            f.write(cmd)
                            f.write("\n")
                        print(f"获取{name}成功")
                    except:
                        continue
            else:
                continue


if __name__ == '__main__':
    ck = ""
    iq = iqy(ck)
    iq.run()
