前面部分将数据库的操作讲述了一遍，注意部分我们终于可以看到些真实的东西了，而不是数据...数据...数据...
##### 创建 django 视图
###### 普通视图
1. 首先在应用文件夹下创建 urls.py 文件，用来配置视图的 url，然后我们需要在项目下的 urls.py 文件中将该应用的 urls 配置进去
   ```python
   # 在项目下 urls.py 文件配置应用的 urls.py 文件
   from django.conf.urls import url, include
   from django.contrib import admin

   urlpatterns = [
       url(r'^admin/', admin.site.urls),
       # include 作用：在 django 匹配 url 时候匹配完 blog/ 后，再次匹配下层地址，所以在 blog/ 
       # 后面不可以添加 "$" 符号，不然会导致不能匹配到地址，namespace 为了区分不同应用下同名的模版
       url(r'^blog/', include('blog.urls', namespace="blog")),
   ]
   ```
2. 在应用文件夹下的 views.py 文件中加入视图
   ```python
   from django.http import HttpResponse

   def home(request):
       return HttpResponse("Hello django")
   ```
3. 在应用下的 urls.py 文件中将视图文件配置进去
   ```python
   from django.conf.urls import url
   from . import views

   # 加上 app_name, 值同 include 中 namespace 的值，否则可能会找不到 url
   app_name = 'blog'
   urlpatterns = [
   	# 当模版引用本地 url 时候需要用到 name 字段值，例如
   	# <a href="{% url 'blog:home' %}"><b>Home</b></a>
       url(r'^home$', views.home, name=home),
   ]
   ```
4. 命令行将代码运行
   ```powershell
   python manage.py runserver 192.168.x.xxx:8080
   ```
   然后可以通过网址 "http://192.168.x.xxx:8080/blog/index" 访问编写的界面，应该是下面这个样子的(原谅我偷懒没有改 ip)![第一个 django 界面](https://upload-images.jianshu.io/upload_images/2888797-c2d7b65db8223a2e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


5. 当 url 中带入参数进行传递时，例如

   ```python
   def hours_ahead(request, offset):
    try:
        offset = int(offset)
    except ValueError as e:
        print(e)
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    return HttpResponse("{} hours later is {}".format(offset, dt))
   ```

   那么我们在 url 配置的时候需要将 offset 参数传入到 url 中去，需要涉及到正则表达式

   ```python
   urlpatterns = [
   	# ?P<offset> 为传递的参数字段名，紧随其后的是参数值的匹配正则
   	# 可以通过 http://192.168.x.xxx:8080/time/ahead/(offset)/ 来访问相应网址
       url(r'^time/ahead/(?P<offset>\d{1, 2})/$', view.hours_ahead, name="time_ahead")
   ]
   ```
   ![带参数](https://upload-images.jianshu.io/upload_images/2888797-d5448f356d5fcf59.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

   reverse() 在配置 url 时候的大用处(这里先提下，项目中会接触到)
   ```python
   # 假设我们有个网址为 192.168.x.xxx:8080/post/1/ 其中 1 为 post 的 id 根据 id 不同显示不同 post
   # 网址的正则为 url(r'post/(?P<pk>[0-9]+)/$', view.post, name="post_detail")
   class Post(models.Model):
   	title = models.CharField("标题", max_length=100)
   	
   	def get_post_url(self):
   		# reverse 会自动指向 'blog:post_detail' 所指向的 url，kwargs 为传入的参数值
   		return reverse('blog:post_detail', kwargs={'pk': self.pk})
   ```

   上面我们提到了正则表达式，这里把 python 常用的正则语法列一下，方便学习

   |  语法  |                 说明                 |  表达式  | 匹配 |
   | :----: | :----------------------------------: | :------: | :--: |
   | 字符串 |               匹配自身               |   abc    | abc  |
   |   .    |         匹配换行符外任意字符         |   a.c    | abc  |
   |   \    |     转义字符，使字符改变原来意思     |   a\.c   | a.c  |
   |   []   |  字符集，对应位可以是字符集任意字符  |  a[bc]d  | acd  |
   |   \d   |             数字：[0-9]              |   o\do   | o2o  |
   |   \D   |                非数字                |   a\Dc   | a,c  |
   |   \s   |  空白字符[<Space>, \t,\r,\n,\f,\v]   |   a\sc   | a c  |
   |   \S   |              非空白字符              |   a\Sc   | abc  |
   |   \w   |        单词字符：[A-Za-z0-9_]        |   a\wc   | abc  |
   |   \W   |              非单词字符              |   a\Wc   | a c  |
   |   *    |    匹配前一个字符串 0 或者无限次     | c[acv]*  |  c   |
   |   +    |    匹配前一个字符串 1 或者无限次     | c[acv]+  |  ca  |
   |   ?    |     匹配前一个字符串 0 或者 1 次     |   cc?    |  c   |
   |  {m}   |        匹配前一个字符串 m 次         |  ac{2}   | acc  |
   | {m, n} |      匹配前一个字符串 m 到 n 次      | ac{1, 3} | acc  |
   |   ^    | 匹配字符串开头，必须以紧随的字符开头 |   ^abc   | abc  |
   |   $    |            匹配字符串末尾            |   abc$   | abc  |
   |   \|   |      表示左右表达式任意匹配一个      | abc\|def | def  |

书写界面的时候，我们不可能每次都去 view 界面写，而且在 view 界面写也不能给页面增加特效，接着就需要发挥模版的作用了

###### 使用模版创建视图

1. 首先在项目根目录下创建 templates 文件夹，用来放视图模版，然后在项目下的 settings.py 文件中注册 templates 文件夹，使 django 能够在 templates 文件夹中找到相应的模版，在 TEMPLATES 中的 DIRS 列表中加入如下代码
   ```python
   'DIRS': [os.path.join(BASE_DIR, 'templates')],
   ```

2. 在 templates 文件夹下再创建放应用模版的文件夹 例如 blog ，然后在 blog 创建 index.html 作为 index 视图的模版
   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <title>{{ title }}</title>
   </head>
   <body>
   <h1>{{ welcome }}</h1>
   </body>
   </html>
   ```

3. 修改视图文件函数
   ```python
   from django.shortcuts import render

   def index(request):
   	# context 中的参数名和模版中 {{ }} 包裹的相同
   	return render(request, 'blog\index.html', context={
           'title': "My Blog Home",
           'welcome': "Welcome to My Blog"
   	})
   	
   # 或者可以用以下方法来写
   def index(request):
   	title = "My Blog Home"
   	welcome = "Welcome to My Blog"
   	return render(request, 'blog\index.html', locals())
   ```
   然后我们就可以看到如下的界面，django 会把 view 的值传到模版中去

   ![第一次使用模版](https://upload-images.jianshu.io/upload_images/2888797-99a3d2fad9cfa623.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

   使用模版的话，我们就需要了解一下模版内置的标签和过滤器，这对我们日后的开发可以提高很多效率

4. django 内置模版标签
   > 1. {% extends %} 继承模版标签
   >
   > 2. 用两个大括号括起来的文字 (例如 {{ post_title }}) 称为变量 (variable)，这意味着在此处插入指定变量的值
   >
   > 3. {% if %} [{% else %} 可省略] {% end if%} 标签
   >
   >    - {% if %} 标签接受 and, or 或者 not 关键字来对多个变量做判断，或者对变量取反 (not)；
   >    - 不允许在同一个标签中同时使用 and 和 or，但可以多次使用同一个逻辑操作符；
   >    - 不支持用圆括号来组合比较操作；
   >    - 没有 {% elif %} 标签，只能 {% if %} 嵌套达到效果；
   >    - 一定要用 {% endif %} 关闭每一个 {% if %} 标签
   >
   >    eg:
   >
   >    ```html
   >    {% if {{ str }} %}
   >    	<p>Value is not null</p>
   >    {% else %}
   >    	<p>Value is null</p>
   >    {% endif %}
   >    ```
   >
   > 4. {% for %} [{% empty %} 可省略] {% endfor %} 标签
   >
   >    - 给标签增加一个 reversed 使得该列表被反向迭代  eg: {% for s in s_list reversed%}
   >
   >    - 可以嵌套使用 {% for %} 标签
   >
   >    - 执行循环之前通常先检测列表的大小，因此 for 标签支持一个可选的 {% empty %} 分句
   >
   >    - 不支持 break 和 continue，退出循环时候，可以改变正在迭代的变量，让其仅仅包含需要迭代的项目。
   >
   >    - 每个 {% for %} 循环里有一个称为 forloop 的模板变量，这个变量存在一些表示循环进度信息的属性，模板解析器碰到{% endfor %}标签后，forloop就不可访问了
   >
   >      > forloop.counter/counter0
   >      >
   >      > 循环的执行次数的整数计数器，从1/0开始计数
   >      >
   >      > forloop.revcounter/revcounter0
   >      >
   >      > 循环执行后的剩余项数量，首次执行为总数/总数减一，最后置为1/0
   >      >
   >      > forloop.first/last    首次/最后一次迭代为 True
   >      >
   >      > forloop.parentloop    当前循环的上一级循环的 forloop 对象的引用(嵌套循环情况下)
   >
   >    eg:
   >
   >    ```html
   >    {% for country in countries %}
   >    	<table>
   >    	{% for city in country %}
   >    		<tr>
   >    		<td>Country {{ forloop.parentloop.counter }}</td>
   >    		<td>City {{ forloop.counter }}</td>
   >    		<td>{{ city }}</td>
   >    		</tr>
   >    	{% endfor %}
   >    	</table>
   >    {% empty%}
   >    	<p>There is no country</p>
   >    {% endfor %}
   >    ```
   >
   >     {% ifequal/ifnotequal%} [{% else %}可省略]  {% endifqual/ifnotequal%} 标签	
   >
   >    比较两个变量的值并且显示一些结果，支持可选的 {% else%} 标签；只有模板变量，字符串，整数和小数可以作为 {% ifequal %} 标签的参数
   >
   > 5. {% autoescape %}{% endautoescape %} 关闭代码块中的自动转义，父类已经关闭则子类也关闭

5. django 常用内置模版过滤器
   模板过滤器是在变量被显示前修改它的值的一个简单方法，以 "|" 拼接，过滤器的参数跟随冒号之后并且总是以双引号包含，例如 {{ value|add:"2" }} 返回值为 value + 2 的值
   > add:"n"，对象相加，如果是数字则是数字加法，列表则是列表的和，无法相加为空。
   >
   > addslashes，增加反斜杠，处理 Javascript 文本非常有用
   >
   > truncatewords:"n"，显示变量前 n 个字符
   >
   > pluralize:"y, ies"，单词的复数形式，可以通过参数设置复数形式
   >
   > date:"xxx"，按指定的格式字符串参数格式化 date 或者 datetime 对象，例如 {{ pub| date:"F j, Y" }}	length，返回变量的长度；对于列表，返回列表元素的个数。对于字符串，返回字符串中字符的个数
   >
   > safe，当系统设置 autoescaping 打开的时候，该过滤器使得输出不进行 escape 转换
   >
   > striptags，删除 value 中的所有 HTML 标签
   >
   > .......

6. django 自定义过滤器和标签
   1. 在应用目录下创建 templatetags 文件夹，同时建立空文件 __ init __.py 和过滤器文件 例如 custom_filter.py 
   2. 在 custom_filter.py 文件中添加过滤器
   ```python
   from django import template
   from blog.models import Category
   # register 是 template.Library 的实例，是所有注册标签和过滤器的数据结构
   register = template.Libary()

   # 自定义过滤器
   @register.filter
   def get_value(dic, key_name):
   	return dic.get(key_name)
   	
   @register.filter
   def get_attr(d, m):
   	if hasattr(d, m):
   		return getattr(d, m)
       
   # 自定义标签
   @register.simple_tag
   def get_all_category
   	return Category.objects.all()
   ```

   **引用自定义过滤器时需要先导入再使用**

   ```html
   {% load custom_filter %}
   <html lang="en">
   <body>
   	<h1>{{ articles|get_value:"article"|get_attr:"id" }}</h1>
       {% get_all_category as category_list%}
       <ul>
           {% for category in category_list%}
           	<li>
                   <a href="#">{{ category.name }}</a>
           	</li>
           {% empty %}
           	There is no category!
           {% endfor%}
       </ul>
   </body>
   </html>
   ```
   最终所展现的效果是这样的(这边只放一部分效果，整体效果可以下载项目自行运行查看)![使用过滤器添加分类列表](https://upload-images.jianshu.io/upload_images/2888797-484be5f05be72101.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

###### 静态文件处理

静态文件主要包括我们需要用到的 css，js 文件等，使用静态文件我们只需要以下两步即可
1. 在应用目录下创建 static 文件夹，可以将常用的 css 文件，js 文件等放入该文件夹

2. 在需要引用静态文件的模版中做如下处理
   ```html
   {# 引入静态文件，只有加载标签模版后才能使用 {% static %} 标签 #}
   {% load staticfiles %}
   {# 在需要引入的地方引入相应文件，例如在 static 文件夹下有个 blog 文件夹，需要引用其 #}
   {# 中的 css/bootstrap.min.css 文件可以通过如下方式进行引入 #}
   <link rel="stylesheet" href="{% static 'blog/css/bootstrap.min.css' %}">
   ```
   最后附上整个项目的地址：[blog_project](https://github.com/kukyxs/blog_project)