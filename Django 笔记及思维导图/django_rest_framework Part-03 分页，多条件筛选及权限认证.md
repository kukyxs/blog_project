#####一. 接口数据分页

上一部分我们通过基本类重构了 view，接着我们需要对返回的数据设置分页，否则单页返回的数量过多也不好处理。

######1. 设置全局分页参数

我们可以在 project 下的 settings.py 文件中加入 REST_FRAMEWORK 字典，设置全局的分页参数

```python
REST_FRAMEWORK = {
    # 配置全局分页类型和每页数量
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
}
```

######2. 不同 view 设置不同分页

我们也可以在不同的 view 下设置不同的分页参数，分页的类我们可以通过继承已有的 Pagination 或者 BasePagination 来写，然后通过 pagination_class 指定

``````python
# 自定义 Pagination，每个 Pagination 的属性不同，可以通过源码查看，然后修改需要的属性
from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page"
``````

```python
# 将自定义的 pagination 类设置到 pagination_class
class PostViewSet(viewsets.ModelViewSet):
    # ....
    # 在 rest_framework.pagination 模块中有多种 Pagination，可以根据具体需求选择
    # [PageNumberPagination, CursorPagination, DjangoPaginator, LimitOffsetPagination]
    # 也可以是自定义的 Pagination 类
    pagination_class = StandardPagination
```

#####二. 接口数据多条件筛选 

目前我们的接口要查找特定的信息只能通过 id 来查找，这肯定是不够完善的，这部分将设置接口的多条件查询

首先我们需要安装过滤器的模块 ```pip install django-filter```

然后我们需要将过滤器模块到 settings.py 中的 INSTALLED_APPS 进行注册才可以使用。注册完以后，我们在 REST_FRAMEWORK 字典中将过滤器添加进去

``````python
REST_FRAMEWORK = {
    # 配置全局分页类型和每页数量
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    # 配置过滤器
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',)
}
``````

基本配置完后我们需要对我们的 viewSet 做些修改，增加一个 filter_backends 属性和 filter_fields 属性

``````python
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = (DjangoFilterBackend, )
    # 使用 title 作为另一个筛选条件
    filter_fields = ['title']
``````

然后运行项目，我们可以通过网址 http://192.168.x.xxx:8080/api/posts/?title="xxxxxx"&format=json 进行访问，可以得到筛选的结果。但是有个问题就是只能精确查询才可以，如果你输入的参数不完整，就查询不到，接下来，我们尝试着完成模糊查询。

首先我们要先创建一个 filters.py 文件，用来定义过滤器 filter

`````python
import django_filters

# 自定义过滤器需要继承 django_filters.rest_framework.FilterSet 类来写
class PostFilter(django_filters.rest_framework.FilterSet):
    # 定义进行过滤的参数，CharFilter 是过滤参数的类型，过滤器参数类型还有很多，包括
    # BooleanFilter，ChoiceFilter，DateFilter，NumberFilter，RangeFilter..等等
    # field_name 为筛选的参数名，需要和你 model 中的一致，lookup_expr 为筛选参数的条件
    # 例如 icontains 为 忽略大小写包含，例如 NumberFilter 则可以有 gte，gt，lte，lt，
    # year__gt，year__lt 等
    title = django_filters.CharFilter('title', lookup_expr='icontains')
    
    # 指定筛选的 model 和筛选的参数，其中筛选的参数在前面设置了筛选条件，则根据筛选条件来执行，
    # 如果为指定筛选条件，则按照精确查询来执行
    class Meta:
        model = Post
        fields = ['title', 'create_time', 'author']
`````

然后我们在 viewSet 指定 FilterClass

`````python
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = (DjangoFilterBackend, )
    # 指定筛选类
    filter_class = PostFilter
`````

rest_framework 的 filter_backends 还有 SearchFilter，OrderingFilter，DjangoObjectPermissionsFilter 等，有兴趣的可以查看官网 [filtering](http://www.django-rest-framework.org/api-guide/filtering/#example)

##### 三. rest_framework 权限设置

到目前为止我们写的接口不设置任何权限上的设置，任何人都可以进行修改，显然不符合某些情况，这部分将对权限方面做些设置。

首先，我们对 model 类进行一些小的改造

``````python
# models.py
# 省略 import
class Post(models.Model):
    # ....省略之前的字段
    # 添加 author 字段，author 我们使用 django 自带的 User 类，
    # 我们通过 ForeignKey 进行关联两个 Model，related_name 为反向引用，
    # 即我们在 User 表内可以通过 related_name 的值来引用 post 对象
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
``````

对数据库做迁移工作后我们对 serializer 类做些相应的修改

``````python
# serializers.py
# ...省略 import
class UserSerializer(serializers.ModelSerializer):
    # posts 字段是反向引用，必须要显示声明出来才可以
    posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())
    
    class Meta:
        model = User
        fields = ['id', 'username', 'posts']
        
class PostSerializer(serializer.ModelSerializer):
    # 显示 author 中的某个字段，例如 username，我们可以通过 source 参数设置
    author = serializer.ReadOnlyField(source='author.usernam')
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'excerpt', 'author', 'create_time', 'modified_time']
``````

现在我们给相应的视图增加访问权限

``````python
# views.py
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # 通过元组增加权限类，IsAuthenticatedOrReadOnly 类未登录只读或者登陆后无权限只读
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
``````

修改后我们运行项目，并通过 httpie 进行一些读取和修改的操作

```http http://192.168.x.xxx:8080/api/posts/``` 能够正常返回的 post 列表

接着我们做 post 提交试试， 自行完善参数值，注意在 posts/ 后有个空格

``````
http Post http://192.168.x.xxx:8080/api/posts/ title="new_post"&......
``````

然后我们会得到一个 json 数据 {"detail": "身份认证信息未提供。"} 显然被拒绝访问了，同样我们操作 DELETE 等操作也是一样，接着我们通过用户名登陆后再操作

``````
http -a [username]:[password] POST http://192.168.x.xxx:8080/api/posts/ title="new_post"&......
``````

然后我们就可以写入等操作了，但是目前这个权限有个缺点，就是不是 post 下的 author 登陆后也可以对 post 进行操作修改，我们重新通过继承 BasePermission 重写一个权限类，限制只能由 post 下的 author 进行修改操作

``````python
# 创建一个 permissions.py 文件，然后把我们的权限写在该文件下
class IsPostAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 通过源码可以知道 SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
        if request.method in permissions.SAFE_METHODS:
            return True
        # 除了 SAFE_METHOD 外的方法我们通过判断是否为该 post 下对应的 author
        return request.user == obj.author
``````

接着我们把自定义的 permission 放到相应视图下

``````python
class PostViewSet(viewsets.ModelViewSet):
    # .....
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsPostAuthorOrReadOnly)
``````

然后我们通过别的用户名对该接口做修改信息的操作，很显然也被拒绝了。

##### 四. rest_framework 身份认证

当我们设置权限的时候，我们不可能每个接口都去设置用户登录，所以就涉及用户身份验证，Android App 常用的身份验证是 Token 验证，所以这部分主要讲 TokenAuthentication，rest_framework 的认证还包括许多，可以查看官网[Authentication](http://www.django-rest-framework.org/api-guide/authentication/)

首先我们需要在 settings.py 文件中配置 TokenAuthentication

``````python
# 首先在 INSTALLED_APPS 注册 authtoken
INSTALLED_APPS = [
    # ....
    'rest_framework',
    'rest_framework.authtoken',
]

# 然后在 REST_FRAMEWORK 字典中配置 DEFAULT_AUTHENTICATION_CLASSES
REST_FRAMEWORK = {
    # 配置全局为 token 验证
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}
``````

配置完后我们需要做数据库的迁移工作，生成 token 的数据库  ```python manage.py migrate``` 生成数据库后，我们需要对已经存在的用户生成 token

``````python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

users = User.objects.all()
for user in users:
    # 生成 token
    token, created = Token.objects.get_or_create(user=user)
    print user.username, token.key
``````

当然，我们不可能每次创建用户的时候都手动去生成 token，接着我们需要在 models.py 文件中加入如下代码

`````python
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
`````

接着我们需要配置 url，用于返回 token 值

``````python
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    url(r'^login/$', obtain_auth_token, name='get_author_token'),
]
``````

配置完后我们可以运行项目，通过 httpie 进行访问调试，注意该页面不允许 GET 访问

```http POST http://192.168.x.xxx:8080/api/login/ username=xxx password=xxxxx```

然后我们能够查看到返回结果类似

``````json
{ "token": "d72251c39dba2b164db18480cfbccefbcc82bbc1" }
``````

当我们获取到 token 后保存到 SharePreference 中，每次访问都在请求头带上 token 值，就不需要每次通过账号密码登录才有权限。

之前我们做删除等编辑操作在 httpie 都是如下操作的

`````
http -a[username]:[password] DELETE http://192.168.x.xxx:8080/api/post/10/
`````

获得 token 后，我们可以通过如下操作，也可以达到相同的效果

``````
http DELETE http://192.168.x.xxx:8080/api/post/10/ "Authorization: Token [your_token_value]"
``````

如果 obtain_auth_token 不满足需求，我们需要返回更多的字段，那我们可以自定义 AuthToken，首先我们先查看 obtain_auth_token 的源码，然后根据源码进行修改

``````python
class ObtainAuthToken(APIView):
	# 限流类
    throttle_classes = ()
    # 权限类
    permission_classes = ()
    # 解析类
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    # 渲染类
    renderer_classes = (renderers.JSONRenderer,)
    # 序列化类
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        # 获取序列化类实例
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        # 获取序列化实例中的 user 参数，用来创建 token
        user = serializer.validated_data['user']
        # 创建 token
        token, created = Token.objects.get_or_create(user=user)
        # 返回 json 渲染
        return Response({'token': token.key})

obtain_auth_token = ObtainAuthToken.as_view()
``````

那我们自定义的认证类就可以继承 ObtainAuthToken 来实现，重写 post 方法即可

``````python
# views.py
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid()
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.pk, 'user_name': user.username})
``````

然后在 url 绑定我们自己的认证类即可