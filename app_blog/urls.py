from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index),
    path('login', views.login),
    path('logout', views.logout),
    path('project', views.project, name="project"),
    path('module', views.module, name="module"),
    path('testcase', views.testcase, name="testcase"),
    re_path('testCaseDetail/(?P<testcase_id>[0-9]+)', views.test_case_detail, name="testCaseDetail"),
    re_path('moduleTestCases/(?P<module_id>[0-9]+)/$', views.module_testcases, name="moduleCases"),
    path('testsuit', views.testsuit, name="testsuit"),
    re_path('managesuit/(?P<suit_id>[0-9]+)', views.managesuit, name="managesuit"),
    re_path('suitcases/(?P<suit_id>[0-9]+)', views.show_testsuit_cases, name="suitcases"),
    path('testCaseExecuteRecord', views.test_case_execute_record, name="testCaseExecuterecord"),
    re_path('diffCaseResponse/(?P<test_record_id>[0-9]+)', views.diffCaseResponse, name="diffCaseResponse"),
    re_path('exceptionInfo/(?P<execute_id>[0-9]+)$', views.show_exception, name="showException"),
    path('testSuitExecuteRecord', views.test_suit_execute_record, name="testSuitExecuteRecord"),
    re_path('suitCaseExecuteRecord/(?P<suit_record_id>[0-9]+)', views.suit_case_execute_record,
            name="suitCaseExecuteRecord"),
    re_path('diffSuiteCaseResponse/(?P<suite_case_record_id>[0-9]+)', views.diffSuiteCaseResponse,
            name="diffSuiteCaseResponse"),
    re_path('suitCaseExecuteException/(?P<suit_case_record_id>[0-9]+)', views.suit_case_execute_exception,
            name="suitCaseExecuteException"),
    re_path('testSuitStatistics/(?P<suit_id>[0-9]+)', views.test_suit_statistics, name="testSuitStatistics"),
    re_path('moduleStatistics/(?P<module_id>[0-9]+)', views.module_statistics, name="moduleStatistics"),
    re_path('projectStatistics/(?P<project_id>[0-9]+)', views.project_statistics, name="projectStatistics"),
]
