# coding utf-8
import requests
import pprint
import json

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

# アクセスするAPIのURI
API_URI_GET_CURRENT = "https://api.webstorage.jp/v1/devices/current"

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

access_param_info = load_access_info()
response = requests.post(API_URI_GET_CURRENT, json.dumps(access_param_info), headers={'Content-Type': 'application/json', 'X-HTTP-Method-Override': 'GET'})

# debug
pprint.pprint(response.json())

receive_data = json.loads(response.text)

