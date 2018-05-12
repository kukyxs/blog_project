上一部分，我们已经提到这篇会讲 views 的代码优化，在这之前，我们先适当了解下 DRF 中的 Request 和 Response。

1. Request 继承 HttpRequest，里面有个 request.data 属性，可以处理任意数据，例如 'POST'，'PUT'，'PATCH'，其用法类似表单中的 request.POST (参考 django 表单部分)
2. Response 是一种 TemplateResponse 采用未呈现的内容，通过内容协商来确定正确的内容类型以返回给客户端，用法直接 return Response(data) 即可

了解完 Request 和 Response 我们将分别通过 @api_view，APIView 和通用视图类对 view 进行一些改造

######1. api_view 注解重构

``````python
# ....import 省略

# 将该视图的请求方法写在注解中，表示该接口只接受列表内的请求方式
@api_view(['GET', 'POST'])
def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        # 通过 Response 展示相应的数据
        return Response(serializer.data)
    elif requets.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # 引入 status 模块，比数字标识符更加直观
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
``````

然后运行项目，输入网址后，所展示的界面和之前的不同了，多了以下部分

> ```
> HTTP 200 OK
> Allow: GET, POST, OPTIONS
> Content-Type: application/json
> Vary: Accept
> ```

这些返回项，而且页面也不是 json了![优化后的列表接口信息](https://upload-images.jianshu.io/upload_images/2888797-b0d64edd2499c3d2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)我们继续做一些修改，在 post_list 函数中加入 format 参数，默认值设置为 None，接着我们对 url 也做一些修改，通过 ```format_suffix_patterns``` 函数对接口返回的信息进行一些处理

``````python
# ....import 省略
app_name = 'api'

urlpatterns = [
    # url(r'^posts/$', views.post_list, name='api_posts'),
    url(r'^post/(?P<pk>[0-9]+)/$', views.post_detail, name='api_post'),
]
# 增加这一行，这样我们就不需要逐一地添加对格式支持的 url 样式
urlpatterns = format_suffix_patterns(urlpatterns)
``````

然后我们对我们接口请求的网址做些修改，在我们之前请求的网址末尾加入 .json **记得去除最末尾的 "/"**，然后我们又可以看到修改前返回的 json 格式数据啦(这边就不贴图啦~)。对于 detail 接口的修改我们也可以根据对 list 的修改进行相应修改，不做多余解释。

###### 2. APIView 重构

``````python
# ....import 省略
class PostList(APIView):
    # 定义 GET 请求的方法，内部实现相同 @api_view
    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 定义 POST 请求的方法
    def post(self, requets, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
``````

然后对 url 进行部分修改即可

``````python
urlpatterns = [
    url(r'^posts/$', views.PostList.as_view(), name='posts'),
]

urlpatterns = fromat_suffix_patterns(urlpatterns)
``````

然后我们又可以看到和上一个例子一样的界面

###### 3. 通过 mixins 和 generics 重构(这个代码够少喔，效果是一样的)

``````python
class PostListMixins(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     generics.GenericAPIView):
    # 指定列表
    queryset = Post.objects.all()
    # 指定序列化类
    serializer_class = PostSerializer
    
    def get(self, request, *args, **kwargs):
        # list 方法继承 ListModelMixin 而来
        return self.list(self, request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        # create 方法继承 CreateModelMixin 而来
        return self.create(self, request, *args, **kwargs)

# detail 视图通过 mixins 和 generics 改造
class PostDetailMixin(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      generics.GenericAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(self, request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(self, request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(self, request, *args, **kwargs)
``````

###### 4. 通用的基于类重构(代码更少，少到想哭，不信继续看)

``````python
# 列表视图
class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

# detail 视图
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
``````

######5. 通过 ViewSet 重构 view，通过 Routers 重构 url (也是少到可以哭的程度，最后效果也是一样的)

首先我们通过继承 ViewSet 来重构 view 类

``````python
class PostViewSet(viewset.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    # 推荐重写该方法，默认返回 status.HTTP_204_NO_CONTENT，
    # 会返回空信息，个人觉得不方便判断，当然按照个人喜好决定
	def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post is not None:
            post.delete()
            return Response({"message": "delete succeed", "code": "200"}, 
                            status=status.HTTP_200_OK)
        return super(PostViewSet, self).destroy(self, request, *args, **kwargs)
``````

然后我们通过 Routers 来重构 url 

``````python
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'posts', view.PostViewSet)
router.register(r'post', view.PostViewSet)

# 然后我们需要在 project 下的 url 中去配置 router
from blog_api.urls import router as blog_api_router

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(blog_api_router.urls)),
]
``````

真是人比人，气死人，代码居然到最后少了那么多，至于为什么，我们来看下 ModelViewSet 的源码吧(兄 dei 别排斥源码啊，这里真的很少很少的，但是又能让我们知道到底做了什么事)  

``````python
class ModelViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
``````

看到这是不是，觉得我们之前的优化都是一步接着一步来的，那我们继续看下 ModelMixin 的源码好了

``````python
class CreateModelMixin(object):
    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        # 根据上传的参数，判断是否有效的 serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 保存 serializer
        self.perform_create(serializer)
        # 返回响应头信息
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class ListModelMixin(object):
    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            # 返回该页的列表
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        # 没有分页则全部展示
        serializer = self.get_serializer(queryset, many=True)
        # 渲染 json 
        return Response(serializer.data)


class RetrieveModelMixin(object):
    """
    Retrieve a model instance.
    """
    def retrieve(self, request, *args, **kwargs):
        # 根据回传的 id 查找
        instance = self.get_object()
        # 将 instance 渲染成 json 展示
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UpdateModelMixin(object):
    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # 更新 instance 的值
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # 保存更新后的数据
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class DestroyModelMixin(object):
    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 删除数据
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

``````
其实内部的具体实现还是我们上一部分写的那些东西，接着，我觉得有必要把自己在 Android 端做的接口测试代码和运行结果贴出来，不然你们又会觉得我坑你们了......这边我为了偷懒(嗯对的，就是偷懒)，我又写了一个只有单个字段的 model

![Android 端 api](https://upload-images.jianshu.io/upload_images/2888797-e11117d912027c90.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![获取列表](https://upload-images.jianshu.io/upload_images/2888797-5c3317f2c773e10e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)![获取列表结果](https://upload-images.jianshu.io/upload_images/2888797-5abddbdd6b7530ae.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![新建数据](https://upload-images.jianshu.io/upload_images/2888797-7cdaa9c87512fa9d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)![新建数据返回结果](https://upload-images.jianshu.io/upload_images/2888797-549eb448bc91cd40.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![获取详情](https://upload-images.jianshu.io/upload_images/2888797-57b69ac0d895b570.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)![获取详情返回结果](https://upload-images.jianshu.io/upload_images/2888797-142bce2a38aaffcd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![更新详情](https://upload-images.jianshu.io/upload_images/2888797-f8fbbbc5afe2b618.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)![更新详情返回结果](https://upload-images.jianshu.io/upload_images/2888797-cd4383f46b9768af.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![删除数据](https://upload-images.jianshu.io/upload_images/2888797-be32d82940ac8e85.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)![删除数据返回结果](https://upload-images.jianshu.io/upload_images/2888797-db3e1b84d3efd760.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

在结束文章的最后，记录自己写的时候遇到的一个坑，当更新 ManyToMany 字段的时候，我们需要重新写 post 方法，**直接传 id 是不能更新的，直接传 id 是不能更新的，直接传 id 是不能更新的(三遍三遍三遍)**。

``````python
# 假设我们的 post 有一个 ManyToMany 字段 tags
class PostDetailView(APIView):
    
    # 更新的时候，需要约定好 ManyToMany 字段的 id 回传时候以什么方式间隔，例如我们用 "," 分隔
    def put(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            # 记得先 clear，然后判断是否上传了 id，上传了 id 需要判断是否多个
            post.tags.clear()
            if request.data['tags']:
                if "," in request.data['tags']:
                    # 我们需要提取 request.data 中 tags 所对应的值，然后通过切割字符串取出 id
                    for i in request.data['tags'].split(","):
                        post.tags.add(i)
                else:
                    post.tags.add(request.data['tags'])
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
``````

在 url 中还是之前的那样绑定

``````python
urlpatterns = [
    url(r"^post/(?P<pk>[0-9]+)/&", views.PostDetailView.as_view(), name="api_post"),
]
``````

修改完后我们就可以开心的更新 M2M 字段了，httpie 命令行如下

``````
http -a [username]:[password] PUT http://192.168.x.xxx:8080/api/post/9/ ...tags=1,2...
``````