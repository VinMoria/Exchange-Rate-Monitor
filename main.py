import requests
from bs4 import BeautifulSoup
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import sys
sys.stdout.reconfigure(line_buffering=True)


with open("config.json") as f:
	config_dict = json.load(f)

HOST = config_dict["HOST"]
SENDER = config_dict["SENDER"]
PASSWORD = config_dict["PASSWORD"]
RECEIVERS = config_dict["RECEIVERS"]
FIXED_THRESHOLD = config_dict["FIXED_THRESHOLD"]

def time_now():
	return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def get_singapore_exchange_rate():
	url = "https://www.boc.cn/sourcedb/whpj/index.html"

	try:
		response = requests.get(url)
		response.encoding = 'utf-8'
		if response.status_code == 200:
			html = response.text
			# 解析HTML
			soup = BeautifulSoup(html, 'html.parser')

			# 找到包含新加坡元汇率信息的行
			rows = soup.find_all('tr')
			singapore_sell_rate = None
			for row in rows:
				cells = row.find_all('td')
				if cells and '新加坡元' in cells[0].text:
					singapore_sell_rate = cells[3].text.strip()  # 第4个<td>是现汇卖出价
					break

			if singapore_sell_rate:
				print(f"新加坡元现汇卖出价: {singapore_sell_rate}")
				return float(singapore_sell_rate)/100
			else:
				print("未找到新加坡元的汇率信息。")
		else:
			print("Failed to retrieve data.")

	except Exception as e:
		print(f"An error occurred: {e}")
		
	return None

def send_email(title, body):
	try:
		message = MIMEMultipart()
		message.attach(MIMEText(body, 'plain'))
		message['From'] = "Exchange Rate Monitor <1123174024@qq.com>"
		message['To'] = SENDER
		message['Subject'] = title

		smtp_obj = smtplib.SMTP(HOST, 587)  # 创建SMTP实例
		
		smtp_obj.starttls()
		smtp_obj.ehlo()
		smtp_obj.login(SENDER, PASSWORD)  # 登入邮箱服务器
		smtp_obj.sendmail(SENDER, RECEIVERS, message.as_string())  # 邮件发出
		print("发送 <" + title + "> 时间：", end="")
		print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		smtp_obj.quit()
	except Exception as e:
		print(f"An error occurred: {e}")


if __name__ == '__main__':
	threshold = FIXED_THRESHOLD
	while True:
		rate_now = get_singapore_exchange_rate()
		print("\n-----------------------")
		print(f"当前时间：{time_now()}")

		if rate_now is not None:
			if rate_now < threshold:
				threshold = rate_now - 0.01
				body = f"{rate_now: .4f} - 当前汇率\n浮动阈值：{threshold}， 固定阈值：{FIXED_THRESHOLD}"
				title = "新币汇率监控"
				send_email(title, body)
				
				print("汇率低于浮动阈值，邮件已发送，浮动阈值被覆盖")

			elif rate_now > FIXED_THRESHOLD:
				threshold = FIXED_THRESHOLD
				print("汇率高于固定阈值，浮动阈值重置")

			else:
				print("汇率高于浮动阈值")

		time.sleep(600)
