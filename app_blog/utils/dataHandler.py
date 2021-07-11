# encoding=utf-8
import re
import hashlib
import os
import json
import traceback
import redis
from interface_test_platform.settings import redis_port

# 初始化框架工程中的全局变量，存储在测试数据中的唯一值数据
# 框架工程中若要使用字典中的任意一个变量，则每次使用后，均需要将字典中的value值进行加1操作。

pool = redis.ConnectionPool(host='localhost', port=redis_port, decode_responses=True)
redis_obj = redis.Redis(connection_pool=pool)


def get_unique_number_value(unique_number):
    print('in get_unique_number_value fun')
    data = None
    try:
        redis_value = redis_obj.get(unique_number)  # {"unique_number": 666}
        print("redis_value: {}".format(redis_value))
        if redis_value:
            data = redis_value
            print("全局唯一数当前生成的值是：%s" % data)
            # 把redis中key为unique_number的值进行加一操作，以便下提取时保持唯一
            redis_obj.set(unique_number, int(redis_value) + 1)
        else:
            data = 10021
            redis_obj.set(unique_number, data)
            print("redis_obj.get(unique_number): {}".format(redis_obj.get(unique_number)))
    except Exception as e:
        print("获取全局唯一数变量值失败，请求的全局唯一数变量是%s,异常原因如下：%s" % (unique_number, traceback.format_exc()))
        data = None
    finally:
        return data


def md5(s):
    m5 = hashlib.md5()
    m5.update(s.encode("utf-8"))
    md5_value = m5.hexdigest()
    return md5_value


# 将请求数据中包含的${变量名}的字符串部分，替换为唯一数或者全局变量字典中对应的全局变量
def data_handler(global_key, requestData):
    try:
        if re.search(r"\$\{unique_num\d+\}", requestData):  # 匹配用户名参数，即"${www}"的格式
            var_name = re.search(r"\$\{(unique_num\d+)\}", requestData).group(1)  # 获取用户名参数
            print("var_name:%s" % var_name)
            var_value = get_unique_number_value(var_name)
            print("var_value: %s" % var_value)
            requestData = re.sub(r"\$\{unique_num\d+\}", str(var_value), requestData)
            var_name = var_name.split("_")[1]
            print("var_name: %s" % var_name)
            print("os.environ[global_key] before asignment in data_handler : {}".format(os.environ[global_key]))
            # "xxxkey" : "{'var_name': var_value}"
            global_var = json.loads(os.environ[global_key])
            global_var[var_name] = var_value
            print("global_var[var_name]  before asignment in data_handler : {}".format(global_var[var_name]))

            os.environ[global_key] = json.dumps(global_var)
            print("os.environ[global_key] after assignment in data_handler : {}".format(os.environ[global_key]))

        if re.search(r"\$\{\w+\(.+\)\}", requestData):  # 匹配密码参数,即"${xxx()}"的格式
            var_pass = re.search(r"\$\{(\w+\(.+\))\}", requestData).group(1)  # 获取密码参数
            print("var_pass: %s" % var_pass)
            print("eval(var_pass): %s" % eval(var_pass))
            requestData = re.sub(r"\$\{\w+\(.+\)\}", eval(var_pass), requestData)  # 将requestBody里面的参数内容通过eval修改为实际变量值
            print("替换函数调用后，requestData: %s" % requestData)  # requestBody是拿到的请求时发送的数据

        if re.search(r"\$\{(\w+)\}", requestData):
            print("all mached data: %s" % (re.findall(r"\$\{(\w+)\}", requestData)))
            for var_name in re.findall(r"\$\{(\w+)\}", requestData):
                print("替换参数化变量之前 requestData: %s" % requestData)
                print("json.loads(os.environ[global_key])[var_name]: {}".format(
                    json.loads(os.environ[global_key])[var_name]))
                requestData = re.sub(r"\$\{%s\}" % var_name, str(json.loads(os.environ[global_key])[var_name]),
                                     requestData)
                print("替换参数化变量之后 requestData: %s" % requestData)
        return 0, requestData, ""
    except Exception as e:
        print("数据处理发生异常，error：{}".format(traceback.format_exc()))
        return 1, {}, traceback.format_exc()


def response_data_post_handler(global_key, response_data, extract_var):
    print("response_data in response_data_post_handler: %s" % response_data)
    print("extract_var: %s" % extract_var)
    if extract_var.lower().find("None") >= 0:
        return
    var_name = extract_var.split("||")[0]
    print("var_name: %s" % var_name)
    regx_exp = extract_var.split("||")[1]
    print("regx_exp: %s" % regx_exp)
    if re.search(regx_exp, response_data):
        print("var_name: %s" % var_name)
        global_vars = json.loads(os.environ[global_key])
        print("global_vars  before asignment in response_data_post_handler : {}".format(global_vars))
        global_vars[var_name] = re.search(regx_exp, response_data).group(1)
        print("global_vars after assignment in response_data_post_handler : {}".format(global_vars))
        os.environ[global_key] = json.dumps(global_vars)
        print("os.environ[global_key]: {}".format(os.environ[global_key]))
    return


# 测试代码
if __name__ == "__main__":
    print(get_unique_number_value("unique_num1"))
