import requests
import json
# from Util.Log import logger


def api_request(url,request_method,request_content):
    #此函数封装了get请求、post和put请求的方法
    if request_method=="get":
        try:
            if isinstance(request_content,dict):
                print("请求的接口地址是：%s" %url)
                print("请求的数据是：%s" %request_content)
                r=requests.get(url, params=json.dumps(request_content))

            else:
                r=requests.get(url+str(request_content))
                print("请求的接口地址是：%s" % r.url)
                print("请求的数据是：%s" % request_content)

        except Exception as e:
            print("get 方法请求发生异常：请求的 url 是 %s,请求的内容是%s\n发生的异常信息如下：%s" %(url,request_content,e))
            r = None
        return r
    elif request_method=="post":
        try:
            if isinstance(request_content,dict):
                print("请求的接口地址是：%s" %url)
                print("请求的数据是：%s" %json.dumps(request_content))
                r = requests.post(url, data=json.dumps(request_content))
            else:
                raise ValueError
        except ValueError as e:
            print("post 方法请求发生异常：请求的 url 是 %s,请求的内容是%s\n发生的异常信息如下：%s" % (url, request_content, "请求参数不是字典类型"))
            r = None
        except Exception as e:
            print("post 方法请求发生异常：请求的 url 是 %s,请求的内容是%s\n发生的异常信息如下：%s" %(url,request_content,e))
            r= None
        return r
    elif request_method=="put":
        try:
            if isinstance(request_content,dict):
                print("请求的接口地址是：%s" %url)
                print("请求的数据是：%s" %json.dumps(request_content))
                r = requests.put(url, data=json.dumps(request_content))
            else:
                raise ValueError
        except ValueError as e:
            print("put 方法请求发生异常：请求的 url 是 %s,请求的内容是%s\n发生的异常信息如下：%s" % (url, request_content, "请求参数不是字典类型"))
            r = None
        except Exception as e:
            print("put 方法请求发生异常：请求的 url 是 %s,请求的内容是%s\n发生的异常信息如下：%s" %(url,request_content,e))
            r= None
        return r
