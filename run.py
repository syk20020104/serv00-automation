import os
import paramiko
import requests
import json
from datetime import datetime, timezone, timedelta

def ssh_multiple_connections(hosts_info, command):
    users = []
    hostnames = []
    for host_info in hosts_info:
        hostname = host_info['hostname']
        username = host_info['username']
        password = host_info['password']
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=hostname, port=22, username=username, password=password)
            stdin, stdout, stderr = ssh.exec_command(command)
            user = stdout.read().decode().strip()
            users.append(user)
            hostnames.append(hostname)
            ssh.close()
        except Exception as e:
            print(f"用户：{username}，连接 {hostname} 时出错: {str(e)}")
    return users, hostnames

ssh_info_str = os.getenv('SSH_INFO', '[]')
hosts_info = json.loads(ssh_info_str)

command = 'whoami'
user_list, hostname_list = ssh_multiple_connections(hosts_info, command)
user_num = len(user_list)
content = "SSH服务器登录信息：\n"
for user, hostname in zip(user_list, hostname_list):
    content += f"用户名：{user}，服务器：{hostname}\n"
beijing_timezone = timezone(timedelta(hours=8))
time = datetime.now(beijing_timezone).strftime('%Y-%m-%d %H:%M:%S')
menu = requests.get('https://api.zzzwb.com/v1?get=tg').json()
loginip = requests.get('https://api.ipify.org?format=json').json()['ip']
content += f"本次登录用户共： {user_num} 个\n登录时间：{time}\n登录IP：{loginip}"

push = os.getenv('PUSH')

def mail_push(url):
    data = {
        "body": content,
        "email": os.getenv('MAIL')
    }

    response = requests.post(url, json=data)

    try:
        response_data = json.loads(response.text)
        if response_data['code'] == 200:
            print("推送成功")
        else:
            print(f"推送失败，错误代码：{response_data['code']}")
    except json.JSONDecodeError:
        print("连接邮箱服务器失败了")

def telegram_push(message):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
    payload = {
        'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
        'text': message,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({
            "inline_keyboard": menu,
            "one_time_keyboard": True
         })
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"发送消息到Telegram失败: {response.text}")

if push == "mail":
    mail_push('https://zzzwb.us.kg/test')
elif push == "telegram":
    telegram_push(content)
else:
    print("推送失败，推送参数设置错误")





import os
import requests

# 定义发送企业微信消息的函数
def send_wechat_message(webhook_url, message):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    response = requests.post(webhook_url, headers=headers, json=data)
    if response.ok:
        print("企业微信消息发送成功")
    else:
        print(f"企业微信消息发送失败，状态码：{response.status_code}，错误信息：{response.text}")

# 从环境变量中获取企业微信Webhook URL
wechat_webhook_url = os.getenv('WECHAT_WEBHOOK_URL')

# 此处content变量应包含您要推送的消息内容
# 假设您已经有了content变量，例如：
# content = "SSH服务器登录信息：\n用户名：user1，服务器：hostname1\n用户名：user2，服务器：hostname2\n本次登录用户共：2 个\n登录时间：2024-08-02 00:42:21\n登录IP：101.47.8.237"

# 调用函数发送消息到企业微信
if wechat_webhook_url:
    send_wechat_message(wechat_webhook_url, content)
else:
    print("未设置企业微信Webhook URL，跳过消息发送。")

