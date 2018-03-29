##### 一. Django 环境配置 (需要搭建 python 环境)

打开 cmd 并输入命令行（以 django 1.10.6 为例）

```pip install django==1.10.6```

安装成功命令行会出现如下提示

```Installing collected packages: django```

```Successfully installed django-1.10.6```

安装完成后输入命令行

```python```

```import django```

```print(django.get_version())```

配置成功则会在控制台打印出 django 的版本号

##### 二. Django 项目创建

找到 .......\Python\Python36\Lib\site-packages\django\bin 下的 django-admin.py 文件

打开命令行切换到项目文件夹，然后输入命令行创建 project

```python .......\Python\Python36\Lib\site-packages\django\bin\django-admin.py ```

```startproject blog_project```

创建成功后，找到项目下的 manage.py 文件，命令行输入

```python manage.py runserver```

打开 "http://127.0.0.1:8000" 即可看到提示成功创建 Django-powered page

Django 默认支持英语，打开配置文件 settings.py 做如下修改以支持中文

```python
LANGUAGE_CODE = 'en-us'  =>  LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'UTC'		=>  TIME_ZONE = 'Asia/Shanghai'
```

再次打开网址，就会显示中文

创建完项目后，需要用户名登录后台管理系统，用户创建可通过如下命令行创建(需要在项目文件下操作)

```python manage.py createsuperuser```

创建完用户名后，可以通过"http://127.0.0.1:8000/admin" 登录后台管理系统

如果说要修改服务器地址端口号，可如下命令行进行操作

```python manage.py runserver 8080```

如果要修改服务器地址，首先需要将修改后的服务器地址写入项目下 settings.py 文件下 ALLOWED_HOSTS[] 列表内，然后通过命令行切换服务器地址

```python manage.py runserver 192.168.0.1:8080```

##### 三. 创建 Django 应用

命令行输入(在 project 文件夹下操作)

```python manage.py startapp blog```

然后在 settings.py 中的 INSTALLED_APPS 列表中注册 'blog' 应用

修改默认数据库，在 settings.py 中的 DATABASES 列表，做如下修改，将默认的 sqlite 数据库改为 mySql 数据库

```python
'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
# ===>
'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'blog_project_db',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306',
    }
```

如果安装的 python 为 python3 以下，需要安装 mysqldb

如果为 python3 以上版本，需要安装 pymysql，命令行如下

```pip install pymysql```

会自动下载安装最新的 pymysql，然后在项目下的 init 文件中加入如下代码

```python
import pymysql
pymysql.install_as_MySQLdb()
```

让 Django 支持 MySql 数据库