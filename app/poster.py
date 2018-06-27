# -*- coding: utf-8 -*-
__author__ = 'shenwei'

import sys

"""测试REST API接口
"""

import urllib
import urllib2
import cookielib
import time

HOST_URL='127.0.0.1:8686'
test_data = {'src-dir':'/home/shenwei/src',"tmp-dir":'/tmp',"dst-dir":"/home/shenwei/dst"}
etl_test_data = {'src-dir':'/home/shenwei/data/myphone.json.ktr','task-name':'my-tester'}

req_post_url = "http://%s/api/v1.0/cli/" % HOST_URL
req_etl_task_post_url = "http://%s/api/v1.0/etl-task/" % HOST_URL
req_get_etl_task_status_url = "http://%s/api/v1.0/etl-task-status/" % HOST_URL
req_get_url = "http://%s/api/v1.0/status/?page=19640419" % HOST_URL

req_openstack_post_url = "http://192.168.1.100:80/dashboard/auth/login"
openstack_auth = {
'csrfmiddlewaretoken':'EjwcRy0vhUtqw1GNA2pMa4vqYzIh49hk',
'fake_email':'',
'fake_password':'',
'next':'/dashboard/',
'region':'http://192.168.1.100:5000/v2.0',
'username':'admin',
'password':'ce39b7ef7d86461b',
}

req_cmf_post_url = "http://10.0.1.37:7180/j_spring_security_check"
cmf_auth = {
	"j_username":"admin",
	"j_password":"admin",
	"returnUrl":"",
	"submit":"",
}

print(">>> GET <<<")
req = urllib2.Request(url = req_get_url)
res_data = urllib2.urlopen(req)
res = res_data.read()
print res

print(">>> POST[cli] <<<")
if len(sys.argv)==2:
    test_data["cmd"] = sys.argv[1]
test_data_urlencode = urllib.urlencode(test_data)
req = urllib2.Request(url = req_post_url,data =test_data_urlencode)
res_data = urllib2.urlopen(req)
res = res_data.read()
print res

print(">>> POST[etl] <<<")
test_data_urlencode = urllib.urlencode(etl_test_data)
req = urllib2.Request(url = req_etl_task_post_url,data =test_data_urlencode)
res_data = urllib2.urlopen(req)
res = res_data.read()
print res

time.sleep(5)

print(">>> GET <<<")
req = urllib2.Request(url = req_get_etl_task_status_url)
res_data = urllib2.urlopen(req)
res = res_data.read()
print res

'''
print(">>> POST[openstack-login] <<<")
test_data_urlencode = urllib.urlencode(openstack_auth)
req = urllib2.Request(url = req_openstack_post_url,data =test_data_urlencode)
res_data = urllib2.urlopen(req)
res = res_data.read()
print res

print(">>> POST[cmf-login] <<<")
test_data_urlencode = urllib.urlencode(cmf_auth)
req = urllib2.Request(url = req_cmf_post_url,data =test_data_urlencode)
res_data = urllib2.urlopen(req)
res = res_data.read()
print res
cookies = res_data.headers["Set-Cookie"]
print cookies
'''
