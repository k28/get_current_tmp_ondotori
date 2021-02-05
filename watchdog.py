# coding utf-8
import requests
import pprint
import json
import time
import os

# API KEYなどのアクセス情報を記載したファイルのパス
ACCESS_INFO_FILE_PATH = "/var/tmp/webstorage.json"
"""
ファイルは以下の形式を想定
{
    "api_key":"xxxxxxxxxxxxxxxxxxxxxxxxx",
    "user_id" : "rbacXXXX",
    "user_pass" : "*******"
    "_comment" : "OndotoriWebStorage API Key and view only account info"
}
"""

# 死活監視で停止中と判断された機器の一覧を保持するファイルパス
STOPED_DEVICE_LIST_PATH = "/var/tmp/webstorage_watchdog_info.json"
"""
ファイルは以下の形式(機器情報はWebStorageから取得した情報をそのまま保持する)
{
    "devices" : [
        {
            "name" : "device_name",
            "serial" : "device_serial",
            "unixtime" : "last_data_unixtime"
        },
        :
    ]
}
"""

# アクセスするAPIのURI
API_URI_GET_CURRENT = "https://api.webstorage.jp/v1/devices/current"

# 死活監視の閾値, この時間を超えて現在値データが更新されていない場合にエラーと判定する
WATCH_THRESHOLD = 3600 * 3

# 死活監視しないモデル(定期的に通信してこない機器は対象から外す)
WATCH_DOG_IGNORE_MODELS = {"TR41", "TR42", "TR45"}

def load_access_info():
    """ WebStorageにアクセスするための情報をファイルから読み込む """
    info_path = ACCESS_INFO_FILE_PATH
    f = open(info_path, 'r')
    load_info = json.load(f)

    api_info = {}
    api_info["api-key"]    = load_info["api_key"]
    api_info["login-id"]   = load_info["user_id"]
    api_info["login-pass"] = load_info["user_pass"]

    return api_info

def load_stopped_devices():
    """停止している機器情報をファイルから読み込む"""
    if os.path.exists(STOPED_DEVICE_LIST_PATH):
        f = open(STOPED_DEVICE_LIST_PATH, 'r')
        load_info = json.load(f)
        return load_info
    else:
        defaul_devices_info = {"devices": []}
        return defaul_devices_info

def write_stopped_devices(info):
    """停止している機器情報をファイルに書き込む"""
    f = open(STOPED_DEVICE_LIST_PATH, 'w')
    json.dump(info, f, ensure_ascii=False, indent=4)
    f.close()

def is_device_exist(serial, stop_device_info):
    for info in stop_device_info["devices"]:
        if info["serial"] == serial:
            return True
    return False

def add_device_to_stopped_list(device, stop_device_info):
    stop_device_info["devices"].append(device)

def remove_form_stop_list(serial, stop_device_info):
    for info in stop_device_info["devices"]:
        if info["serial"] == serial:
            stop_device_info["devices"].remove(info)
            return

def watchdog(current_info):
    """現在値情報から機器からの通信が途絶えていないか調べる"""
    stop_device_info = load_stopped_devices() 
    
    current_time = time.time()
    for device in current_info["devices"]:
        if device["model"] in WATCH_DOG_IGNORE_MODELS:
            continue
        serial = device["serial"]
        name = device["name"]
        last_access_unixtime = device["unixtime"]
        if (current_time - float(last_access_unixtime)) > WATCH_THRESHOLD:
            if not is_device_exist(serial, stop_device_info):
                pprint.pprint("No Response: " + serial + " " + name + " ")
                add_device_to_stopped_list(device, stop_device_info)
                # TODO: 通信が途絶えている機器を見つけた時の処理
        else:
            if is_device_exist(serial, stop_device_info):
                # TODO: 通信が途絶えていた機器が復帰した
                pprint.pprint("Recoverd: " + serial + " " + name + " ")
                remove_form_stop_list(serial, stop_device_info)

    # 機器情報を保存する
    write_stopped_devices(stop_device_info)
    

access_param_info = load_access_info()
response = requests.post(API_URI_GET_CURRENT, json.dumps(access_param_info), headers={'Content-Type': 'application/json', 'X-HTTP-Method-Override': 'GET'})

# debug
#pprint.pprint(response.json())

watchdog(response.json())

receive_data = json.loads(response.text)

