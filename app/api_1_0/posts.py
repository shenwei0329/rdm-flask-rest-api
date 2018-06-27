# -*- coding: utf-8 -*-
#
#   REST API 服务
#   =============
#   by shenwei. 2018.6 @ChengDu
#

from flask import jsonify, request, g, abort, url_for, current_app
from . import api
import commands
import thread
import uuid
import json

work_manager = thread.WorkManager()
job_q = {}


def addJobQ(uuid, jobname, cmd, log, scheduler, status):
    global job_q
    job_q[uuid] = {'jobname':jobname, 'cmd':cmd, 'log':log, 'scheduler':scheduler, 'status':status}
    Save()


def delJobQ(jobname):
    global job_q
    uuid_list = []
    for uuid in job_q:
        if job_q[uuid]['jobname'] == jobname:
            uuid_list.append(uuid)
    for uuid in uuid_list:
            del job_q[uuid]
    Save()


def dispEnv():
    global task_q, job_q
    print task_q
    print job_q
    #pass


@api.route('/cli/', methods=['POST'])
def new_cli_post():
    """
        用POST提交一个表单，里面以“字典”方式存放接口参数

        POST请求：执行一次 CLI 命令。注：该接口要注意安全使用。

    :return: 返回信息
    """

    """
        问题总能从网上得到答案：request.form的类型是 ImmutableMultiDict，必须通过 to_dict() 转换成 dict
    """
    post = request.form.to_dict()

    """
    TODO 在这里添加对表单的处理
        例如：执行一个CLI命令，最好以线程方式做（这时需要考虑异步响应）
    """
    if post.has_key("cmd"):
        _status,_str = commands.getstatusoutput(post["cmd"])

        post["status"] = _status
        if _status==0:
            post["cmd-response"] = _str
        else:
            post["cmd-response"] = "ERR:<%s>" % _str
    else:
        post['cmd-response'] = "None"
    return jsonify(post)

@api.route('/etl-task/', methods=['POST'])
def new_etl_task_post():
    """
        用POST提交一个表单，里面以“字典”方式存放接口参数

        POST请求：启动一次 ETL 任务过程

    :return: 返回信息
    """

    global work_q

    """
        问题总能从网上得到答案：request.form的类型是 ImmutableMultiDict，必须通过 to_dict() 转换成 dict
    """
    post = request.form.to_dict()

    """
        执行 pan.sh 脚本
        如何把 脚本 的执行过程和结果 友好 的反馈给UI？因执行需要一定的时间等待，所以这里最好能使用消息通知方式到UI

        每次运行都会将执行日志输出到指定的文件中，UI可以查看
    """
    print(">>> 1...<<<")

    """ 查找是否已存在该任务的 uuid
    """
    _uuid = getUUIDbyName(post['task-name'])
    if _uuid=='':
        _uuid = str(uuid.uuid4())

    _log_path = '/root/data/log/etl-task-%s.log' % _uuid
    """ 清除旧日志内容
    """
    _cmd = "rm %s" % _log_path
    commands.getstatusoutput(_cmd)
    print(">>> 1.1...[%s]" % _log_path)
    if post.has_key('cmd'):
        _cmd = post['cmd'] + ' ' + post['src-dir'] + ' > ' + _log_path
    else:
        _cmd = '/home/shenwei/data-integration/pan.sh -file "%s" -log "%s"' % (post["src-dir"], _log_path)
    print(">>> 2...[%s].[%s]<<<" % (_cmd, post['task-name']))

    """ 需要引入 线程池
    """
    addTaskQ(_uuid,post['task-name'],_log_path,'RUNNING')

    dispEnv()

    work_manager.add_task(_cmd, _uuid)
    """
    _status,_str = commands.getstatusoutput(_cmd)
    """
    print(">>> 3...<<<")
    post["status"] = 0
    post["result"] = u"ETL任务提交完成"
    return jsonify(post)

@api.route('/etl-task-delete/', methods=['POST'])
def new_etl_task_delete_post():
    """
        用POST提交一个表单，里面以“字典”方式存放接口参数

        POST请求：删除 ETL 任务

    :return: 返回信息
    """

    global work_q

    """
        问题总能从网上得到答案：request.form的类型是 ImmutableMultiDict，必须通过 to_dict() 转换成 dict
    """
    post = request.form.to_dict()

    """
        执行 pan.sh 脚本
        如何把 脚本 的执行过程和结果 友好 的反馈给UI？因执行需要一定的时间等待，所以这里最好能使用消息通知方式到UI

        每次运行都会将执行日志输出到指定的文件中，UI可以查看
    """
    print(">>> 1...<<<")

    """ 查找是否已存在该任务的 uuid
    """
    _uuid = getUUIDbyName(post['task-name'])
    if _uuid != '':
        delTaskQ(post['task-name'])

    dispEnv()

    print(">>> 2...<<<")
    post["status"] = 0
    post["result"] = u"ETL任务删除完成"
    return jsonify(post)

@api.route('/etl-job/', methods=['POST'])
def new_etl_job_post():
    """
        用POST提交一个表单，里面以“字典”方式存放接口参数

        POST请求：启动一次 ETL 定时任务过程

    :return: 返回信息
    """

    global job_q

    """
        问题总能从网上得到答案：request.form的类型是 ImmutableMultiDict，必须通过 to_dict() 转换成 dict
    """
    post = request.form.to_dict()

    """
        执行 pan.sh 脚本
        如何把 脚本 的执行过程和结果 友好 的反馈给UI？因执行需要一定的时间等待，所以这里最好能使用消息通知方式到UI

        每次运行都会将执行日志输出到指定的文件中，UI可以查看
    """
    print(">>> 1...<<<")

    """ 查找是否已存在该任务的 uuid
    """
    _uuid = getJobUUIDbyName(post['job-name'])
    if _uuid=='':
        _uuid = str(uuid.uuid4())

    _log_path = '/root/data/log/etl-job-%s.log' % _uuid
    """ 清除旧日志内容
    """
    _cmd = "rm %s" % _log_path
    commands.getstatusoutput(_cmd)
    print(">>> 1.1...[%s]" % _log_path)
    _scheduler = post['scheduler']
    print(">>> 1.2...[%s]" % _scheduler)
    if post.has_key('cmd'):
        _cmd = post['cmd'] + ' ' + post['src-dir'] + ' >> ' + _log_path
    else:
        _cmd = '/home/shenwei/data-integration/pan.sh -file "%s" -log "%s"' % (post["src-dir"], _log_path)
    print(">>> 2...[%s].[%s]<<<" % (_cmd, post['job-name']))

    """ 需要引入 线程池
    """
    addJobQ(_uuid,post['job-name'],_cmd,_log_path,_scheduler,'SCHEDULE')

    dispEnv()

    """
    _status,_str = commands.getstatusoutput(_cmd)
    """
    print(">>> 3...<<<")
    post["status"] = 0
    post["result"] = u"ETL作业提交完成"
    return jsonify(post)

@api.route('/etl-job-delete/', methods=['POST'])
def new_etl_job_delete_post():
    """
        用POST提交一个表单，里面以“字典”方式存放接口参数

        POST请求：删除 ETL 定时任务

    :return: 返回信息
    """

    global job_q

    """
        问题总能从网上得到答案：request.form的类型是 ImmutableMultiDict，必须通过 to_dict() 转换成 dict
    """
    post = request.form.to_dict()

    """
        执行 pan.sh 脚本
        如何把 脚本 的执行过程和结果 友好 的反馈给UI？因执行需要一定的时间等待，所以这里最好能使用消息通知方式到UI

        每次运行都会将执行日志输出到指定的文件中，UI可以查看
    """
    print(">>> 1...<<<")

    """ 查找是否已存在该任务的 uuid
    """
    _uuid = getJobUUIDbyName(post['job-name'])
    if _uuid != '':
        delJobQ(post['job-name'])

    dispEnv()

    print(">>> 2...<<<")
    post["status"] = 0
    post["result"] = u"ETL作业删除完成"
    return jsonify(post)

@api.route('/etl-task-resp/', methods=['POST'])
def etl_task_resp():
    """
        用POST提交一个表单，里面以“字典”方式存放接口参数

        POST请求：由 WORKER 返回 ETL 任务执行结果

    :return: 返回信息
    """

    global task_q

    """
        问题总能从网上得到答案：request.form的类型是 ImmutableMultiDict，必须通过 to_dict() 转换成 dict
    """
    post = request.form.to_dict()

    """
        执行 pan.sh 脚本
        如何把 脚本 的执行过程和结果 友好 的反馈给UI？因执行需要一定的时间等待，所以这里最好能使用消息通知方式到UI

        每次运行都会将执行日志输出到指定的文件中，UI可以查看
    """
    dispEnv()
    print(">>> 1...<<<")
    _uuid = post["api-id"]
    _status = post["status"]
    print(">>> 2...[%s][%s]<<<" % (_status,_uuid))

    if task_q.has_key(_uuid):
        if _status == '0':
            task_q[_uuid]['status'] = 'DONE'
        else:
            task_q[_uuid]['status'] = 'ERROR'
    else:
        print(">>> 2.1... No key[%s]<<<" % _uuid)
    print(">>> 3...<<<")
    return jsonify({'result':'OK'})

@api.route('/etl-timer/', methods=['POST'])
def etl_timer():
    """
        用POST提交一个表单，里面以“字典”方式存放接口参数

        POST请求：由 TIMER 发来的时标

    :return: 返回信息
    """

    global job_q, work_manager

    """
        问题总能从网上得到答案：request.form的类型是 ImmutableMultiDict，必须通过 to_dict() 转换成 dict
    """
    post = request.form.to_dict()

    """
        执行 pan.sh 脚本
        如何把 脚本 的执行过程和结果 友好 的反馈给UI？因执行需要一定的时间等待，所以这里最好能使用消息通知方式到UI

        每次运行都会将执行日志输出到指定的文件中，UI可以查看
    """
    dispEnv()
    print(">>> 1...<<<")
    _mon = post['mon']
    _day = post['day']
    _hour = post['hour']
    _min = post['min']
    _week = post['week']

    print(">>> 2...<<<")

    for _uuid in job_q:
        if job_q[_uuid]['status']!='RUNNING':
            if beActive(job_q[_uuid]['scheduler'],[_min,_hour,_day,_mon,_week]):
                work_manager.add_job(job_q[_uuid]['cmd'], _uuid)
                job_q[_uuid]['status'] = 'RUNNING'

    print(">>> 3...<<<")
    return jsonify({'result':'OK'})

def beActive(schedule,date):
    _date = schedule.split(' ')
    print(">>>beActive[%s][%s]" % (_date,date))
    for _i in range(0,5):
        if _date[_i]!='*' and int(_date[_i])!=int(date[_i]):
            return False
    return True

@api.route('/etl-job-resp/', methods=['POST'])
def etl_job_resp():
    """
        用POST提交一个表单，里面以“字典”方式存放接口参数

        POST请求：由 JOB_WORKER 返回 ETL 任务执行结果

    :return: 返回信息
    """

    global job_q

    """
        问题总能从网上得到答案：request.form的类型是 ImmutableMultiDict，必须通过 to_dict() 转换成 dict
    """
    post = request.form.to_dict()

    """
        执行 pan.sh 脚本
        如何把 脚本 的执行过程和结果 友好 的反馈给UI？因执行需要一定的时间等待，所以这里最好能使用消息通知方式到UI

        每次运行都会将执行日志输出到指定的文件中，UI可以查看
    """
    dispEnv()
    print(">>> 1...<<<")
    _uuid = post["api-id"]
    _status = post["status"]
    print(">>> 2...[%s][%s]<<<" % (_status,_uuid))

    if job_q.has_key(_uuid):
        if _status == '0':
            job_q[_uuid]['status'] = 'DONE'
        else:
            job_q[_uuid]['status'] = 'ERROR'
    else:
        print(">>> 2.1... No key[%s]<<<" % _uuid)
    print(">>> 3...<<<")
    return jsonify({'result':'OK'})

@api.route('/etl-task-status/', methods=['GET'])
def get_etl_task_status():
    """
        GET请求：获取所有 ETL 任务过程的状态

    :return: 返回信息
    """

    global task_q

    dispEnv()

    print(">>> start...<<<")
    resp = {}
    for _uuid in task_q:
        resp[task_q[_uuid]['taskname']] = task_q[_uuid]['status']

    print(">>> done...<<<")
    return jsonify(resp)

@api.route('/etl-job-status/', methods=['GET'])
def get_etl_job_status():
    """
        GET请求：获取所有 ETL 作业过程的状态

    :return: 返回信息
    """

    global job_q

    dispEnv()

    print(">>> start...<<<")
    resp = {}
    for _uuid in job_q:
        resp[job_q[_uuid]['jobname']] = job_q[_uuid]['status']

    print(">>> done...<<<")
    return jsonify(resp)

@api.route('/etl-task-log/', methods=['GET'])
def get_etl_task_log():
    """
        GET请求：ETL 任务的执行日志

    :return: 返回信息
    """

    global task_q

    dispEnv()

    print(">>> start...<<<")
    _task = request.args.get('task-name')
    _uuid = getUUIDbyName(_task)
    if _uuid != "":
        _log_file = task_q[_uuid]['log']
        fh = open(_log_file)
        l = []
        for line in fh.readlines():
            l.append(line)
    resp = {'text':l}
    print(">>> done...<<<")
    return jsonify(resp)

@api.route('/etl-job-log/', methods=['GET'])
def get_etl_job_log():
    """
        GET请求：ETL 作业的执行日志

    :return: 返回信息
    """

    global job_q

    dispEnv()

    print(">>> start...<<<")
    _job = request.args.get('job-name')
    _uuid = getJobUUIDbyName(_job)
    if _uuid != "":
        _log_file = job_q[_uuid]['log']
        fh = open(_log_file)
        l = []
        for line in fh.readlines():
            l.append(line)
    resp = {'text':l}
    print(">>> done...<<<")
    return jsonify(resp)

def getUUIDbyName(name):
    """
    根据 任务名称 从task_map表中获取其uuid

    :param name:
    :return:
    """
    global task_q
    for uuid in task_q:
        if task_q[uuid]['taskname'] == name:
            return uuid
    return ""

def getJobUUIDbyName(name):
    """
    根据 任务名称 从task_map表中获取其uuid

    :param name:
    :return:
    """
    global job_q
    for uuid in job_q:
        if job_q[uuid]['jobname'] == name:
            return uuid
    return ""
