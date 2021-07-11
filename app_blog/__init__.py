import pymysql         # 一定要添加这三行！
pymysql.version_info = (1, 3, 13, "final", 0)   #此行在启动出错后有需要在写
pymysql.install_as_MySQLdb()