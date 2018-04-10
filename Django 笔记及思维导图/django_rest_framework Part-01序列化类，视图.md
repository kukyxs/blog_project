#####一. rest_framework 环境配置

通过命令行操作如下语句

```pip install djangorestframework```

看到安装成功的提示就安装成功，可以嗨皮的写 restful 接口了

创建 django 项目，然后创建一个 app，例如 blog_api (不会创建参考 django 部分)

```python manage.py startapp blog_api```

将新建 app 的信息加入到已有项目中

在 settings.py 中的 INSTALLED_APPS 列表中加入如下

``````python
INSTALLED_APPS = [
    # ....
    'rest_framework',
    'blog_api',
    # ....
]
``````

#####二. 创建 rest 的 Serializers 类 

创建 serializer 类之前，我们先在 models.py 文件下创建 model 类（参考 django，不详细解释，直接上代码）

``````python
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=70)
    body = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField()
    excerpt = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.excerpt:
            self.excerpt = strip_tags(self.body)[:50]
		super(Post, self).save(*args, **kwargs)
``````

创建完 model 类后需要创建数据库(参考 django 数据库迁移部分)

```python manage.py makemigrations```

```python manage.py migrate```

然后创建 serializer 类

``````python
from rest_framework import serializers
from .models import Post

# serializer 类需要继承 serializers.Serializer，
# 然后实现父类的 update，create 方法
class PostSerializer(serializers.Serializer):
    # 声明需要被序列化和反序列化的字段，同 model 的字段，
    # 字段名注意需要同 model 字段同名
    title = serializers.CharField(max_length=70)
    body = serializers.CharField()
    create_time = serializers.DateTimeField()
    modified_time = serializers.DateTimeField()
    excerpt = serializers.CharField(max_length=200, allow_blank=True)
    
    # 定义创建方法
    def create(self, validated_date):
        return Post.objects.all()
    
    # 定义修改方法
    def update(self, instance, validated_date):
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.create_time = validated_data.get('create_time', instance.create_time)
        instance.modified_time = validated_data.get('modified_time', instance.modified_time)
        instance.excerpt = validated_data.get('excerpt', instance.excerpt)
``````

Serializer 的常用字段类型类似 Model 类，可以参考 django model 部分的参数，

Serializer 的常用设置参数也类似 Model 类，部分不同，例如 model 中的 blank 和 null 在 serializer 中为 allow_blank 和 allow_null，其余类似，可以参考 django model 部分的设置参数

关于 Serializer 的一些常用操作

``````python
from .models import Post
from .serializers import PostSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.utils.six import BytesIO
import datetime

# 创建数据(参考 django model 部分)
post = Post(title='Restful 接口入门', create_time=datetime.datetime.now(),
            modified_time=datetime.datetime.now(), body='Restful 接口入门',
            excerpt='Restful 接口入门')
# 保存到数据库
post.save()
# 对 post 实例进行序列化
serializer = PostSerializer(post)
# 通过 serializer.data 查看序列化后的结果，是一个字典
# {'title': 'Restful 接口入门', 'body': 'Restful 接口入门', 
# 'create_time': '2018-04-05T21:27:21+08:00', 'modified_time': '2018-04-05T21:27:25+08:00', 
# 'excerpt': 'Restful 接口入门'}
print(serializer.data)

# 通过 JSONRenderer 将序列化的数据渲染成 json 格式的数据
content = JSONRenderer().render(serializer.data)
# b'{"title":"Restful 接口入门","body":"Restful 接口入门",
# "create_time":"2018-04-05T21:27:21+08:00",
# "modified_time":"2018-04-05T21:27:25+08:00","excerpt":"Restful 接口入门"}'
print(content)

# 如果将 json 转回字典，需要通过 BytesIO 进行处理
stream = BytesIO(content)
# 打印结果同序列化后的结果
data = JSONParser().parser(stream)

# 将数据转换成为实体类对象
serializer = PostSerializer(data=data)
# 需要检验是否有效数据，类似 Form
serializer.is_valid()
# 经过验证后的数据，返回一个 OrderedDict
# OrderedDict([('title', 'Restful 接口入门'), ('body', 'Restful 接口入门'),
# ('create_time', datetime.datetime(2018, 4, 5, 21, 27, 21,
# tzinfo=<DstTzInfo 'Asia/Shanghai' CST+8:00:00 STD>)), 
# ('modified_time', datetime.datetime(2018, 4, 5, 21, 27, 25,
# tzinfo=<DstTzInfo 'Asia/Shanghai' CST+8:00:00 STD>)), 
# ('excerpt', 'Restful 接口入门')])
print(serializer.validated_data)
# 保存有效的数据，通常用于 POST 提交的数据信息
serializer.save()

# 除了序列化模型实例，也可以将 queryset 进行序列化，此时需要在 serializer 中加入 many=True
posts = Post.objects.all()
serializer = PostSerializer(posts, many=True)
# 返回 OrderedDict 列表
print(serializer.data)
``````

##### 三. 创建 rest 的 view 函数

rest_framework 类似 django，需要通过 view 来展示接口返回的数据信息，在 views.py 中创建视图函数

``````python
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from .models import Post
from .serializers import PostSerializer

@csrf_exempt
def post_list(request):
    # 如果是 GET 请求则返回所有的列表
	if request.method == "GET":
		posts = Post.objects.all()
		serializer = PostSerializer(posts, many=True)
		return JsonResponse(serializer.data, safe=False) 
    # 如果是 POST 请求则保存数据
    elif request.method == "POST":
         # 将 request 中的参数取出来进行序列化
		data = JSONParser().parse(request)
		serializer = PostSerializer(data=data)
         # 判断是否有效的数据
		if serializer.is_valid():
            # 有效数据保存，返回 201 CREATED
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        # 无效则返回 400 BAD_REQUEST
        return JsonResponse(serializer.errors, status=400)
``````

##### 四. 将视图函数关联到 url

创建 urls.py 文件，然后在 project 下的 urls.py 文件中配置 url (参考 django 部分)

``````python
# project 下的 urls
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 配置 blog_api 的 url
    url(r'^api/', include('blog_api.urls', namespace='api')),
]
``````

``````python
# blog_api 下的 urls
from django.conf.urls import url
from . import views

# 必须加上，且同 project 下 urls 中的 namespace 同值
app_name = 'api'

urlpatterns = [
    url(r'^posts/$', views.post_list, name="api_posts"),
]
``````

配置完 url 运行项目

```python manage.py runserver 192.168.x.xxx:8080```

然后通过网址  http://192.168.x.xxx:8080/api/posts/ 查看 restful 接口

或者可以通过 httpie 来进行接口查看，其好处是可以直接操作 POST 等操作

首先安装 httpie ```pip install httpie```

然后通过命令行输入网址，前面加上 http 即可

```http http://192.168.x.xxx:8080/api/posts/```

然后可以查看接口返回的数据

##### 五. Serializer 的第一次优化调整

写完第一个 restful 接口，是否发现 model 和 serializer 有很多重复的代码，能否进行优化呢，答案是当然可以的

刚才我们的 serializer 类继承 serializers.Serializer 类，这回我们进行修改，通过继承 serializers.ModelSeralizer 实现相同的效果

``````python
# ModelSeralizer 会自动帮我们实现 update 和 create 方法
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        # result 接口需要返回的字段，可以指定 "__all__" 展示全部参数
        fields = ['title', 'body', 'create_time', 'modified_time', 'excerpt']
        # exclude 为不展示的字段名，和 fields 不能同时设置
        # exclude = ['id', 'author']

# 通过继承 serializers.ModelSeralizer 实现的 serializer 其字段可以通过如下进行查看
serializer = PostSerializer()
print(repr(serializer))
``````

别的无需修改，修改完 serializer 类后我们再次运行项目，输入网址查看返回相同的接口信息，而且省了好多重复代码，这才是关键，身为程序员，不会偷懒可不好喔！

如果说需要对某个 post 进行更新，查询，删除等操作，那我们需要一个 detail 类来进行操作

```````python
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser
from .models import Post
from .serializers import PostSerializer

@csrf_exempt
def post_detail(request, pk):
    # 根据 pk 值获取对应的 post 实例
    post = get_object_or_404(Post, pk=pk)
    # 首先判断是否存在这个 post，不存在直接返回 404 NOT FOUND
    # 如果 settings.py 下的 DEBUG 属性设置为 True 的话，django 会不展示 404 页面，设置成 False 即可
    if post is None:
        return HttpResponse(status=404)
    # 如果 request 是 GET 方法，则直接展示对应 pk 的 post
    if request.method == 'GET':
        serializer = PostSerializer(post)
        # 将序列化后的数据转换成 json 展示
        return JsonResponse(serializer.data)
    # 如果 request 是 PUT 方法，则解析 request 中的参数，
    # 进行校验是否合理，合理则更新，否则返回 400 BAD REQUEST
    elif request.method == 'PUT':
        data = JSONParser().parser(request)
        # 更新 post 的值
        serializer = PostSerializer(post, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
    # 如果 request 是 DELETE 方法，则直接删除
    elif request.method == 'DELETE':
        post.delete()
        return HttpResponse(status=204)
```````

url 配置 detail 界面

``````python
app_name = 'api'

urlpatterns = [
    url(r'^posts/$', views.post_list, name="api_posts"),
    url(r'^post/(?P<pk>[0-9]+)/$', views.post_detail, name='api_post'),
]
``````
如果在 model 中存在 ForeignKey 和 MaynToMany 链表结构字段，那我们接口返回的时候只会显示该表中数据的 id 字段，但是很多时候我们需要返回该数据的所有字段，接着我们对 Serializer 进行一些改造，让其可以返回全部的字段。

``````python
# 首先我们在 model 中增加两个链表结构字段，同时创建相关的 model 并生成数据库
class PostModel(models.Model):
    # ....
    author = models.ForeignKey(Author, related_name='posts', on_delete=models.CASCADE)
    tags = models.ManyToMany(Tag, related_name='posts', blank=True)
    
class Author(models.Model):
    username = models.CharField(max_length=100)
    
class Tag(models.Model):
    name = models.CharField(max_length=100)
``````

``````python
# 然后我们需要给新增的 model 创建 serializer
class AuthorSerializer(serializers.ModelSerializer):
    # 会显示所有该 author 下的 posts
    posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())
    
    class Meta:
        model = Author
        fields = '__all__'
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        
class PostSerializer(serializer.ModelSerializer):
    # ForeignKey 链表结构字段处理，有两种处理方式，第一种展示 serializer 中设置的字段，
    # 第二种展示某个指定字段
    # author = AuthorSerializer(read_only=True)
    author = serializer.ReadOnlyField(source="author.username")
    # ManyToMany 链表结构字段处理
    tag = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = '__all__'
``````