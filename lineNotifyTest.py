#文件參考:https://ithelp.ithome.com.tw/articles/10234576#_=_
#官方文件:https://notify-bot.line.me/doc/en/

#基本功能測試
import requests

def lineNotifyMessage(token, msg):

    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code


if __name__ == "__main__":
  token = 'ozF9oFsD4Z3zvtyy9xXHYzd08na4gaT3EZEZGXPmVwC'#AXXMRm1rdxj69E3IWDrKBnatzhhPYrgmvL8G1ikehnV
  message = '基本功能測試'
  lineNotifyMessage(token, message)