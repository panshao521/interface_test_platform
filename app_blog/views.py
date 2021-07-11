import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
import traceback
from django.contrib import auth  # 引入auth模块
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage
from .forms import UserForm
from . import models
from . import tasks


@login_required
def index(request):
    print("request.user.is_authenticated: {}".format(request.user.is_authenticated))
    if not request.user.is_authenticated:
        return redirect("/login")
    return render(request, 'index.html')


def login(request):
    print("request.session.items(): {}".format(request.session.items()))
    if request.session.get('is_login', None):
        return redirect('/')

    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = auth.authenticate(username=username, password=password)
                if user is not None:
                    print("**********" * 10, )
                    auth.login(request, user)
                    request.session['is_login'] = True
                    return redirect('/')
                else:
                    message = "用户名不能存在或者密码不正确！"
            except:
                message = "登录程序出现错误"
                traceback.print_exc()

        return render(request, 'login.html', locals())

    login_form = UserForm()
    return render(request, 'login.html', locals())


@login_required
def logout(request):
    auth.logout(request)
    request.session.flush()
    return redirect("/login")


def get_paginator(request, data):
    paginator = Paginator(data, 10)

    # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
    page = request.GET.get('page')
    try:
        paginator_pages = paginator.page(page)
    except PageNotAnInteger:
        # 如果请求的页数不是整数, 返回第一页。
        paginator_pages = paginator.page(1)
    except InvalidPage:
        # 如果请求的页数不存在, 重定向页面
        return HttpResponse('找不到页面的内容')
    print("----------------", paginator_pages)
    print("----------------", paginator_pages.has_previous())
    print("----------------", paginator_pages.has_next())
    return paginator_pages


def get_server_address(env):
    if env:  # 环境处理
        env_data = models.Configuration.objects.filter(env=env[0])
        print("env_data: {}".format(env_data))
        if env_data:
            ip = env_data[0].ip
            port = env_data[0].port
            print("ip: {}, port: {}".format(ip, port))
            server_address = "http://{}:{}".format(ip, port)
            print("server_address: {}".format(server_address))
            return server_address
        else:
            return ""
    else:
        return ""


@login_required
def project(request):
    print("request.user.is_authenticated: ", request.user.is_authenticated)
    projects = models.Project.objects.filter().order_by('-id')
    print("projects:", projects)
    return render(request, 'project.html', {'projects': get_paginator(request, projects)})


@login_required
def module(request):
    if request.method == "GET":  # 请求get时候，id倒序查询所有的模块数据
        modules = models.Module.objects.filter().order_by('-id')
        return render(request, 'module.html', {'modules': get_paginator(request, modules)})
    else:  # 否则就是Post请求，会根据输入内容，使用模糊的方式查找所有的项目
        proj_name = request.POST['proj_name']
        projects = models.Project.objects.filter(name__contains=proj_name.strip())
        projs = [proj.id for proj in projects]
        modules = models.Module.objects.filter(belong_project__in=projs)  # 把项目中所有的模块都找出来
        return render(request, 'module.html', {'modules': get_paginator(request, modules), 'proj_name': proj_name})


@login_required
def testcase(request):
    print("request.session['is_login']: {}".format(request.session['is_login']))
    testcases = ""
    if request.method == "GET":
        testcases = models.TestCase.objects.filter().order_by('id')
        print("testcases in testcase: {}".format(testcases))
    elif request.method == "POST":
        print("request.POST: {}".format(request.POST))
        test_case_id_list = request.POST.getlist('testcases_list')
        env = request.POST.getlist('env')
        print("env: {}".format(env))
        server_address = get_server_address(env)
        if not server_address:
            return HttpResponse("提交的运行环境为空，请选择环境后再提交！")

        if test_case_id_list:
            test_case_id_list.sort()
            print("test_case_id_list: {}".format(test_case_id_list))
            print("用例获取到，开始用例的执行")
            tasks.run_test_case_task(test_case_id_list, server_address)
        else:
            print("运行测试用例失败")
            return HttpResponse("提交的运行测试用例为空，请选择用例后在提交！")
        testcases = models.TestCase.objects.filter().order_by('id')

    return render(request, 'testcase.html', {'testcases': get_paginator(request, testcases)})


@login_required
def test_case_detail(request, testcase_id):
    testcase_id = int(testcase_id)
    test_case = models.TestCase.objects.get(id=testcase_id)
    print("test_case: {}".format(test_case))
    print("test_case.id: {}".format(test_case.id))
    print("test_case.belong_project: {}".format(test_case.belong_project))
    print("test_case: {}".format(test_case))

    return render(request, 'testCaseDetail.html', {'testcase': test_case})


@login_required
def module_testcases(request, module_id):
    module = ""
    if module_id:  # 访问的时候，会从url中提取模块的id，根据模块id查询到模块数据，在模板中展现
        module = models.Module.objects.get(id=int(module_id))
    testcases = models.TestCase.objects.filter(belong_module=module).order_by('-id')
    print("testcases in module_testcases: {}".format(module_testcases))
    return render(request, 'testcase.html', {'testcases': get_paginator(request, testcases)})


@login_required
def testsuit(request):
    if request.method == "POST":
        count_down_time = 0
        if request.POST['delay_time']:
            print("输入的延迟时间是: {}".format(request.POST['delay_time']))
            try:
                count_down_time = int(request.POST['delay_time'])
            except:
                print("输入的延迟时间是非数字！")
        else:
            print("没有输入延迟时间")
        print(dir(request.POST))
        env = request.POST.getlist('env')
        print("env: {}".format(env))
        server_address = get_server_address(env)
        if not server_address:
            return HttpResponse("提交的运行环境为空，请选择环境后再提交！")
        testsuit_list = request.POST.getlist('testsuit_list')
        if testsuit_list:
            print("------********", testsuit_list)
            for suit_id in testsuit_list:
                test_suit = models.TestSuit.objects.get(id=int(suit_id))
                print("test_suit: {}".format(test_suit))
                username = request.user.username
                test_suit_record = models.TestSuitExecuteRecord.objects.create(test_suit=test_suit,
                                                                               run_time_interval=count_down_time,
                                                                               creator=username)

                tasks.run_test_suit_task(test_suit_record, test_suit, server_address)

        else:
            print("运行测试集合用例失败")
            return HttpResponse("运行的测试集合为空，请选择测试集合后再运行！")

    testsuits = models.TestSuit.objects.filter()
    return render(request, 'testsuit.html', {'testsuits': get_paginator(request, testsuits)})


@login_required
def managesuit(request, suit_id):
    test_suit = models.TestSuit.objects.get(id=suit_id)
    if request.method == "GET":
        testcases = models.TestCase.objects.filter().order_by('id')
        print("testcases:", testcases)
    elif request.method == "POST":
        testcases_list = request.POST.getlist('testcases_list')
        if testcases_list:
            print("------********", testcases_list)
            for testcase in testcases_list:
                test_case = models.TestCase.objects.get(id=int(testcase))
                models.TestSuitTestCases.objects.create(test_suit=test_suit, test_case=test_case)
        else:
            print("添加测试用例失败")
            return HttpResponse("添加的运行测试用例为空，请选择用例后再添加！")
        testcases = models.TestCase.objects.filter().order_by('id')
    return render(request, 'managesuit.html',
                  {'testcases': get_paginator(request, testcases), 'test_suit': test_suit})


@login_required
def show_testsuit_cases(request, suit_id):
    test_suit = models.TestSuit.objects.get(id=suit_id)
    testcases = models.TestSuitTestCases.objects.filter(test_suit=test_suit)
    if request.method == "POST":
        testcases_list = request.POST.getlist('testcases_list')
        if testcases_list:
            print("------********", testcases_list)
            for testcase in testcases_list:
                test_case = models.TestCase.objects.get(id=int(testcase))
                models.TestSuitTestCases.objects.filter(test_suit=test_suit, test_case=test_case).first().delete()
        else:
            print("删除测试集合的测试用例失败")
            return HttpResponse("删除的运行测试用例为空，请选择用例后再进行删除！")
    test_suit = models.TestSuit.objects.get(id=suit_id)
    testcases = models.TestSuitTestCases.objects.filter(test_suit=test_suit)
    return render(request, 'suitcases.html',
                  {'testcases': get_paginator(request, testcases), 'test_suit': test_suit})


@login_required
def test_case_execute_record(request):
    testCaseExecuteRecords = models.TestCaseExecuteRecord.objects.filter().order_by('-id')
    return render(request, 'testCaseExecuteRecord.html',
                  {'testCaseExecuteRecords': get_paginator(request, testCaseExecuteRecords)})


@login_required
def diffCaseResponse(request, test_record_id):
    test_record_data = models.TestCaseExecuteRecord.objects.get(id=test_record_id)
    print("test_record_data: {}".format(test_record_data))
    present_response = test_record_data.response_data
    if present_response:
        print("present_response in db: {}".format(present_response))
        present_response = json.dumps(json.loads(present_response), sort_keys=True, indent=4,
                                      ensure_ascii=False)  # 中文字符不转ascii编码
        print("present_response: {}".format(present_response))
    last_time_execute_response = test_record_data.last_time_response_data
    if last_time_execute_response:
        print("last_time_execute_response in db".format(last_time_execute_response))
        last_time_execute_response = json.dumps(json.loads(last_time_execute_response), sort_keys=True, indent=4,
                                                ensure_ascii=False)
        print("last_time_execute_response after json.dumps "''": {}".format(last_time_execute_response))
    print("last_time_execute_response: {}".format(last_time_execute_response))
    return render(request, 'diffResponse.html', locals())


@login_required
def show_exception(request, execute_id):
    testrecord = models.TestCaseExecuteRecord.objects.get(id=execute_id)
    return render(request, 'exceptionInfo.html', {'exception_info': testrecord.exception_info})


@login_required
def test_suit_execute_record(request):
    test_suit_execute_records = models.TestSuitExecuteRecord.objects.filter().order_by('-id')
    return render(request, 'testSuitExecuteRecord.html',
                  {'test_suit_execute_records': get_paginator(request, test_suit_execute_records)})


@login_required
def suit_case_execute_record(request, suit_record_id):
    test_suit_execute_record = models.TestSuitExecuteRecord.objects.get(id=suit_record_id)
    suit_case_execute_records = models.TestSuitTestCaseExecuteRecord.objects.filter(
        test_suit_record=test_suit_execute_record)
    return render(request, 'suitCaseExecuteRecord.html',
                  {'suit_case_execute_records': get_paginator(request, suit_case_execute_records)})


@login_required
def diffSuiteCaseResponse(request, suite_case_record_id):
    test_record_data = models.TestSuitTestCaseExecuteRecord.objects.get(id=suite_case_record_id)
    print("test_record_data: {}".format(test_record_data))
    present_response = test_record_data.response_data
    if present_response:
        print("present_response in db: {}".format(present_response))
        print("json.loads(present_response): {}".format(json.loads(present_response)))
        present_response = json.dumps(json.loads(present_response), sort_keys=True, indent=4, ensure_ascii=False)
        print("present_response after json.dumps: {}".format(present_response))
    last_time_execute_response = test_record_data.last_time_response_data
    if last_time_execute_response:
        print("last_time_execute_response in db: {}".format(last_time_execute_response))
        last_time_execute_response = json.dumps(json.loads(last_time_execute_response), sort_keys=True, indent=4,
                                                ensure_ascii=False)
        print("last_time_execute_response after json.dumps "''": {}".format(last_time_execute_response))
    print("last_time_execute_response: {}".format(last_time_execute_response))
    return render(request, 'diffResponse.html', locals())


@login_required
def suit_case_execute_exception(request, suit_case_record_id):
    testrecord = models.TestSuitTestCaseExecuteRecord.objects.get(id=suit_case_record_id)
    return render(request, 'exceptionInfo.html', {'exception_info': testrecord.exception_info})


@login_required
def test_suit_statistics(request, suit_id):
    test_suit = models.TestSuit.objects.get(id=suit_id)
    success_num = len(models.TestSuitExecuteRecord.objects.filter(test_suit=test_suit, test_result="成功"))
    fail_num = len(models.TestSuitExecuteRecord.objects.filter(test_suit=test_suit, test_result="失败"))
    test_suit_records = models.TestSuitExecuteRecord.objects.filter(test_suit=test_suit).order_by('-id')
    return render(request, 'testSuitStatistics.html',
                  {'test_suit_records': get_paginator(request, test_suit_records), 'success_num': success_num,
                   'fail_num': fail_num})


@login_required
def module_statistics(request, module_id):
    test_module = models.Module.objects.get(id=int(module_id))
    test_cases = models.TestCase.objects.filter(belong_module=test_module)
    test_suit_success_num = len(
        models.TestSuitTestCaseExecuteRecord.objects.filter(test_case__in=test_cases, execute_result="成功"))
    test_suit_fail_num = len(
        models.TestSuitTestCaseExecuteRecord.objects.filter(test_case__in=test_cases, execute_result="失败"))
    test_case_success_num = len(
        models.TestCaseExecuteRecord.objects.filter(belong_test_case__in=test_cases, execute_result="成功"))
    test_case_fail_num = len(
        models.TestCaseExecuteRecord.objects.filter(belong_test_case__in=test_cases, execute_result="失败"))
    success_num = test_suit_success_num + test_case_success_num
    fail_num = test_suit_fail_num + test_case_fail_num
    return render(request, 'moduleStatistics.html',
                  {'test_module': test_module, 'success_num': success_num, 'fail_num': fail_num})


@login_required
def project_statistics(request, project_id):
    test_project = models.Project.objects.get(id=int(project_id))
    test_cases = models.TestCase.objects.filter(belong_project=test_project)
    test_suit_success_num = len(
        models.TestSuitTestCaseExecuteRecord.objects.filter(test_case__in=test_cases, execute_result="成功"))
    test_suit_fail_num = len(
        models.TestSuitTestCaseExecuteRecord.objects.filter(test_case__in=test_cases, execute_result="失败"))
    test_case_success_num = len(
        models.TestCaseExecuteRecord.objects.filter(belong_test_case__in=test_cases, execute_result="成功"))
    test_case_fail_num = len(
        models.TestCaseExecuteRecord.objects.filter(belong_test_case__in=test_cases, execute_result="失败"))
    success_num = test_suit_success_num + test_case_success_num
    fail_num = test_suit_fail_num + test_case_fail_num
    return render(request, 'projectStatistics.html',
                  {'test_project': test_project, 'success_num': success_num, 'fail_num': fail_num})
