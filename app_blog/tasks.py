from . import models
import time
import os
import traceback
from .utils.dataHandler import *
from .utils.api_request import api_request


def run_test_case_task(test_case_id_list, server_address):
    global_key = 'case' + str(int(time.time() * 100000))
    os.environ[global_key] = '{}'
    print("global_key: {}".format(global_key))
    print("os.environ[global_key]: {}".format(os.environ[global_key]))

    for test_case_id in test_case_id_list:
        test_case = models.TestCase.objects.filter(id=int(test_case_id))[0]
        print("######执行用例: {}".format(test_case))
    last_execute_record_data = models.TestCaseExecuteRecord.objects.filter(
        belong_test_case_id=test_case_id).order_by('-id')
    if last_execute_record_data:
        last_time_execute_response_data = last_execute_record_data[0].response_data
    else:
        last_time_execute_response_data = ''
    print("last_execute_record_data: {}".format(last_execute_record_data))
    print("last_time_execute_response_data: {}".format(last_time_execute_response_data))
    execute_record = models.TestCaseExecuteRecord.objects.create(belong_test_case=test_case)
    execute_start_time = time.time()  # 记录时间戳，便于计算总耗时（毫秒）
    print("execute_start_time: {}".format(execute_start_time))
    execute_record.execute_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_start_time))
    print("execute_record.execute_start_time: {}".format(execute_record.execute_start_time))
    execute_record.last_time_response_data = last_time_execute_response_data
    # 获取当前用例上一次执行结果
    execute_record.save()

    request_data = test_case.request_data
    extract_var = test_case.extract_var
    assert_key = test_case.assert_key
    interface_name = test_case.uri
    belong_project = test_case.belong_project
    belong_module = test_case.belong_module
    maintainer = test_case.maintainer
    request_method = test_case.request_method
    print("request_data: {}".format(request_data))
    print("extract_var: {}".format(extract_var))
    print("assert_key: {}".format(assert_key))
    print("interface_name: {}".format(interface_name))
    print("belong_project: {}".format(belong_project))
    print("belong_module: {}".format(belong_module))
    print("maintainer: {}".format(maintainer))
    print("request_method: {}".format(request_method))
    url = "{}{}".format(server_address, interface_name)
    print("url: {}".format(url))
    code, request_data, error_msg = data_handler(global_key, str(request_data))
    print("request_data: {}".format(request_data))
    if code != 0:
        print("数据处理异常，error: {}".format(error_msg))
        execute_record.execute_result = "失败"
        execute_record.status = 1
        execute_record.exception_info = error_msg
        execute_end_time = time.time()
        execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
        execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
        execute_record.save()
        return
    execute_record.request_data = request_data

    try:
        res_data = api_request(url, request_method, json.loads(request_data))
        print("res_data.json(): {}".format(json.dumps(res_data.json(), ensure_ascii=False)))
        result_flag, exception_info = assert_result(res_data, assert_key)
        # 结果记录保存
        if result_flag:
            print("用例执行成功")
            print('extract_var.strip() != "None": {}'.format(extract_var.strip() != "None"))
            if extract_var.strip() != "None":
                print("extract_var in run_test_case_task: {}".format(extract_var))
                response_data_post_handler(global_key, json.dumps(res_data.json(), ensure_ascii=False), extract_var)

            execute_record.execute_result = "成功"
        else:
            print("用例执行失败")
            execute_record.execute_result = "失败"
            execute_record.exception_info = exception_info
        execute_record.response_data = json.dumps(res_data.json(), ensure_ascii=False)
        execute_record.status = 1
        execute_end_time = time.time()
        execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
        print("execute_record.execute_end_time: {}".format(execute_record.execute_end_time))
        execute_record.execute_total_time = int((execute_end_time - execute_start_time) * 1000)
        print("execute_record.execute_total_time.microseconds: {}".format(execute_record.execute_total_time))
        execute_record.save()

    except Exception as e:
        print("接口请求异常，error: {}".format(traceback.format_exc()))
        execute_record.execute_result = "失败"
        execute_record.exception_info = traceback.format_exc()
        execute_record.status = 1
        execute_end_time = time.time()
        execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
        print("execute_record.execute_end_time: {}".format(execute_record.execute_end_time))
        execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
        print("execute_record.execute_total_time: {}".format(execute_record.execute_total_time))
        execute_record.save()


def run_test_suit_task(test_suit_record, test_suit, server_address):
    global_key = test_suit.suite_desc + str(int(time.time() * 100000))
    # global_vars = {"{}".format(global_key): {}}
    os.environ[global_key] = '{}'
    print("global_key: {}".format(global_key))
    print("os.environ[global_key]: {}".format(os.environ[global_key]))
    test_suit_test_cases = models.TestSuitTestCases.objects.filter(test_suit=test_suit).order_by('id')
    print("test_suit_test_cases: {}".format(test_suit_test_cases))
    test_suit_record.test_result = "成功"
    test_suit_record.execute_start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    for test_suit_test_case in test_suit_test_cases:
        test_case = test_suit_test_case.test_case
        print("######执行用例: {}".format(test_case))
        last_execute_record_data = models.TestSuitTestCaseExecuteRecord.objects.filter(
            test_case_id=test_case.id).order_by('-id')
        if last_execute_record_data:
            last_time_execute_response_data = last_execute_record_data[0].response_data
        else:
            last_time_execute_response_data = ''
        print("last_execute_record_data: {}".format(last_execute_record_data))
        print("last_time_execute_response_data: {}".format(last_time_execute_response_data))
        suite_case_execute_record = models.TestSuitTestCaseExecuteRecord.objects.create(test_suit_record=test_suit_record,
                                                                             test_case=test_case)
        execute_start_time = time.time()  # 记录时间戳，便于计算总耗时（毫秒）
        print("execute_start_time: {}".format(execute_start_time))
        suite_case_execute_record.execute_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_start_time))
        print("suite_case_execute_record.execute_start_time: {}".format(suite_case_execute_record.execute_start_time))
        suite_case_execute_record.last_time_response_data = last_time_execute_response_data
        suite_case_execute_record.save()
        request_data = test_case.request_data
        extract_var = test_case.extract_var
        assert_key = test_case.assert_key
        interface_name = test_case.uri
        belong_project = test_case.belong_project
        belong_module = test_case.belong_module
        maintainer = test_case.maintainer
        request_method = test_case.request_method
        print("request_data: {}".format(test_case.request_data))
        print("extract_var: {}".format(extract_var))
        print("assert_key: {}".format(assert_key))
        print("interface_name: {}".format(interface_name))
        print("belong_project: {}".format(belong_project))
        print("belong_module: {}".format(belong_module))
        print("maintainer: {}".format(maintainer))
        print("request_method: {}".format(request_method))
        url = "{}{}".format(server_address, interface_name)
        print("url: {}".format(url))
        code, request_data, error_msg = data_handler(global_key, str(request_data))
        print("request_data: {}".format(request_data))
        if code != 0:
            print("数据处理异常，error: {}".format(error_msg))
            suite_case_execute_record.execute_result = "失败"
            suite_case_execute_record.status = 1
            suite_case_execute_record.exception_info = error_msg
            execute_end_time = time.time()
            suite_case_execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
            print("suite_case_execute_record.execute_end_time: {}".format(suite_case_execute_record.execute_end_time))
            suite_case_execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
            print("suite_case_execute_record.execute_total_time: {}".format(suite_case_execute_record.execute_total_time))
            suite_case_execute_record.save()
            test_suit_record.test_result = "失败"

        suite_case_execute_record.request_data = request_data
        try:
            res_data = api_request(url, request_method, json.loads(request_data))
            print("json.dumps(res_data.json(): {}".format(json.dumps(res_data.json(), ensure_ascii=False)))

            result_flag, exception_info = assert_result(res_data, assert_key)
            # 结果记录保存
            if result_flag:
                print("用例执行成功")
                suite_case_execute_record.execute_result = "成功"
                print('extract_var.strip() != "None": {}'.format(extract_var.strip() != "None"))
                if extract_var.strip() != "None":
                    print("extract_var in run_test_suit_task: {}".format(extract_var))
                    response_data_post_handler(global_key, json.dumps(res_data.json(), ensure_ascii=False), extract_var)
            else:
                print("用例执行失败")
                suite_case_execute_record.execute_result = "失败"
                suite_case_execute_record.exception_info = exception_info
                test_suit_record.test_result = "失败"
            suite_case_execute_record.response_data = json.dumps(res_data.json(), ensure_ascii=False)
            suite_case_execute_record.status = 1
            execute_end_time = time.time()
            print("execute_end_time: {}".format(execute_end_time))
            suite_case_execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                                                       time.localtime(execute_end_time))
            print("suite_case_execute_record.execute_end_time: {}".format(suite_case_execute_record.execute_end_time))
            print("int((execute_end_time - execute_start_time) * 1000): {}".format(
                int((execute_end_time - execute_start_time) * 1000)))
            suite_case_execute_record.execute_total_time = int((execute_end_time - execute_start_time) * 1000)
            print("suite_case_execute_record.execute_total_time.microseconds: {}".format(
                suite_case_execute_record.execute_total_time))
            suite_case_execute_record.save()
        except Exception as e:
            print("接口请求异常，error: {}".format(e))
            suite_case_execute_record.execute_result = "失败"
            suite_case_execute_record.exception_info = traceback.format_exc()
            suite_case_execute_record.status = 1
            execute_end_time = time.time()
            suite_case_execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
            print("suite_case_execute_record.execute_end_time: {}".format(suite_case_execute_record.execute_end_time))
            suite_case_execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
            print("suite_case_execute_record.execute_total_time: {}".format(suite_case_execute_record.execute_total_time))
            suite_case_execute_record.save()
            test_suit_record.test_result = "失败"

    test_suit_record.status = 1  # 执行完了
    test_suit_record.save()


# 断言处理，有多个断言词的情况
def assert_result(responseObj, key_word):
    '''验证数据正确性'''
    print('key_word in assert_result: {}'.format(key_word))

    try:
        if '&&' in key_word:
            key_word_list = key_word.split('&&')
            print("key_word_list: %s" % key_word_list)
            # 断言结果标识符
            flag = True
            exception_info = ''
            # 遍历分隔出来的断言关键词列表
            for keyWord in key_word_list:
                # 如果断言词非空，则进行断言
                if keyWord:
                    print("json.dumps(responseObj.json())): {}".format(
                        json.dumps(responseObj.json(), ensure_ascii=False)))
                    # 没查到断言词则认为是断言失败
                    if not (keyWord in json.dumps(responseObj.json(), ensure_ascii=False)):
                        print("断言失败，关键词为： %s" % keyWord)
                        flag = False
                        exception_info = "keyword: {} not matched from response, assert failed".format(keyWord)
                    else:
                        print("断言词匹配成功：'{}'".format(keyWord))
            print("flag: %s" % flag)
            if flag:
                print("断言成功")
            return flag, exception_info

        else:
            print("key_word: %s" % key_word)
            if key_word in json.dumps(responseObj.json(), ensure_ascii=False):
                print("断言成功")
                return True, ''
            else:
                print("断言失败，断言词为: %s" % key_word)
                return False, ''
    except Exception as e:
        print("error occurs in assert_result function: %s" % e)
        return False, traceback.format_exc()
