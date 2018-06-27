# !/usr/bin/env python
# -*- coding:utf-8 -*-
# 引入：ref_blog:http://www.open-open.com/home/space-5679-do-blog-id-3247.html
#

import commands
import Queue
import threading

import urllib
import urllib2

import time
from time import *

"""
    2015.8.30 shenwei @Chengdu

    引入队列和线程处理

"""

HOST_URL='127.0.0.1:8000'
req_job_post_url = "http://%s/api/v1.0/etl-job-resp/" % HOST_URL
req_timer_url = "http://%s/api/v1.0/etl-timer/" % HOST_URL


class WorkManager(object):

    def __init__(self):
        self.job_queue = Queue.Queue()
        JobWork(self.job_queue)
        Timer()

    """
        添加一项工作入队
    """
    def add_task(self, cmd, api_id):
        self.work_queue.put({'cmd': cmd, 'api-id': api_id})

    """
        添加一项作业入队
    """
    def add_job(self, cmd, api_id):
        self.job_queue.put({'cmd': cmd, 'api-id': api_id})

    """
        检查剩余队列任务
    """
    def check_queue(self):
        return self.work_queue.qsize()

    """
        等待所有线程运行完毕
    """
    def wait_allcomplete(self):
        pass

class Work(threading.Thread):

    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def notif(self, status, api_id):
        print(">>>notif...[%s][%s]<<<" % (str(status), api_id))
        try:
            data = urllib.urlencode({'status': status, 'api-id': api_id})
            req = urllib2.Request(url=req_etl_task_post_url, data=data)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            print res
        except Exception:
            print('notif: Error!')

    def run(self):
        print("thread start...")
        while True:
            try:
                ''' 采用阻塞方式接收队列
                '''
                item = self.work_queue.get(block=True)
                print("Q.get")
                ''' 执行命令
                '''
                status, str = commands.getstatusoutput(item['cmd'])
                self.work_queue.task_done()
                print("Q.done")
                ''' 将执行状态返回，接口ID＝item['api-id']
                2015.8.31: 用 REST 接口通知！
                '''
                self.notif(status, item['api-id'])
            except Exception:
                print('run: Error!')

class JobWork(threading.Thread):

    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def notif(self, status, api_id):
        print(">>>job notif...[%s][%s]<<<" % (str(status), api_id))
        try:
            data = urllib.urlencode({'status': status, 'api-id': api_id})
            req = urllib2.Request(url=req_etl_job_post_url, data=data)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            print res
        except Exception:
            print('notif: Error!')

    def run(self):
        print("job thread start...")
        while True:
            try:
                ''' 采用阻塞方式接收队列
                '''
                item = self.work_queue.get(block=True)
                print("job.Q.get")
                ''' 执行命令
                '''
                status, str = commands.getstatusoutput(item['cmd'])
                self.work_queue.task_done()
                print("job.Q.done")
                ''' 将执行状态返回，接口ID＝item['api-id']
                2015.8.31: 用 REST 接口通知！
                '''
                self.notif(status, item['api-id'])
            except Exception:
                print('run: Error!')

class Timer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self._min = 99
        self.start()

    def notif(self, mon, day, hour, min, week):
        print(">>>Timer notif...<<<")
        try:
            _param = {'mon':mon, 'day':day, 'hour':hour, 'min':min, 'week':week}
            data = urllib.urlencode(_param)
            req = urllib2.Request(url=req_etl_timer_url, data=data)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            print res
        except Exception:
            print('Timer notif: Error!')

    def run(self):
        print("Timer start...")
        while True:
            ''' 睡眠30秒
            '''
            sleep(30)

            print("Timer step...")

            today = strftime('%Y%m%d %H%M %w', localtime())
            ''' 20150903 1134 4
                012345678901234
            '''
            year = today[0:4]
            mon = today[4:6]
            day = today[6:8]
            hour = today[9:11]
            min = today[11:13]
            week = today[14:15]

            print year + ' ' + mon + ' ' + day + ' ' + hour + ' ' + min + ' ' + week
            if self._min != int(min):
                """ 确保每分钟只通知一次
                """
                self._min = int(min)
                self.notif(mon,day,hour,min,week)
