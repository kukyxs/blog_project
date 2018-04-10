##### Rest 框架的 Request 和 Response 对象，以及视图改造

在 rest 框架中，引入了 Request 对象 和 Response 对象

Request 继承 HttpRequest，里面有个 request.data 属性，可以处理任意数据，例如 'POST'，'PUT'，'PATCH'，其用法类似表单中的 request.POST (参考 django 表单部分)

Response 是一种 TemplateResponse 采用未呈现的内容，通过内容协商来确定正确的内容类型以返回给客户端，用法直接 return Response(data) 即可

了解完 Request 和 Response 我们将对 view 分别通过 @api_view，APIView 和通用视图类对视图进行一些改造

######1. api_view 注解重构

``````python
# ....import 省略

# 将该视图的请求方法写在注解中
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

这些返回项，我们继续做一些修改

在 post_list 函数中加入 format 参数，默认值设置为 None

接着我们对 url 也做一些修改

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

然后我们对我们接口请求的网址做些修改，在我们之前请求的网址末尾加入 .json 或者 .api 记得去除最末尾的 "/"，然后我们又可以看到修改前返回的 json 格式数据啦。对于 detail 接口的修改可以根据 list 进行相应修改，不做多余解释。

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

根据 list 可以修改 detail 的接口 view

###### 3. 通过 mixins 和 generics 重构

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

###### 4. 通用的基于类重构(代码少到想哭，不信继续看)

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

######5. 通过 ViewSet 重构 view，通过 Routers 重构 url (也是少到可以哭的程度)

首先我们通过继承 ViewSet 来重构 view 类

``````python
class PostViewSet(viewset.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    # 推荐重写该方法，默认返回 status.HTTP_204_NO_CONTENT，
    # 会返回空信息，个人觉得不方便判断，当然按照个人喜好决定，不强制
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

OK，重构完毕，真是代码一个比一个少，少到哭。当然并不是说之前多的不如不讲，至少我们知道要如何去创建一个 resultful 接口，至于后面的代码那么少，都是因为框架的功劳啊。

接着我们可以看下 ModelViewSet 的源码(相信很多都不愿意看源码，包括之前自己也是，但是源码的确能够解释清楚很多东西，所以这里还是推荐看源码，不需要每句代码都能懂，大概的意思懂就可以了)

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

其内部的实现原理也是通过继承各种 mixins 的 view 来实现，然后我们看下 mixins 的源码，大概的原理注解解释的应该够清楚

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
看完源码，更加确定我们之前讲的一堆东西并不是没用的。最后附上接口测试的截图 Android 版（有图有真相才行，省的你们出错了打我），为了方便，写了另外的一个只有一个字段的模型
Android Retrofit Api![apis](https://upload-images.jianshu.io/upload_images/2888797-e11117d912027c90.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

获取列表![get_list](https://upload-images.jianshu.io/upload_images/2888797-5c3317f2c773e10e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)![get_list_result](https://upload-images.jianshu.io/upload_images/2888797-5abddbdd6b7530ae.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

新建数据![post_one](https://upload-images.jianshu.io/upload_images/2888797-7cdaa9c87512fa9d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)![post_one_result](https://upload-images.jianshu.io/upload_images/2888797-549eb448bc91cd40.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

获取详情![get_detail](https://upload-images.jianshu.io/upload_images/2888797-57b69ac0d895b570.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)![get_detail_result](https://upload-images.jianshu.io/upload_images/2888797-142bce2a38aaffcd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

更新详情![update_detail](https://upload-images.jianshu.io/upload_images/2888797-f8fbbbc5afe2b618.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)![update_detail_result](https://upload-images.jianshu.io/upload_images/2888797-cd4383f46b9768af.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

删除数据![delete_obj](https://upload-images.jianshu.io/upload_images/2888797-be32d82940ac8e85.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)![delete_obj_result](https://upload-images.jianshu.io/upload_images/2888797-db3e1b84d3efd760.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

最后的最后，自己写的时候遇到的一个坑，记录下吧，更新 ManyToMany 字段的时候，我们需要重新写 post 方法，直接传 id 不能更新。

``````python
# 假设我们的 post 有一个 ManyToMany 字段 tags
class PostDetailView(APIView):
    def get_object(self, pk):
        try:
            return Post.objects.filter(pk=pk)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

	def get(self, request, pk, format=None):
        serializer = PostSerializer(self.get_object(pk), data=request.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
    
    # 建议最后返回的 status 不使用 status.HTTP_204_NO_CONTENT，不方便判断
    def delete(self, request, pk, format=None):
        self.get_object(pk).delete()
        return Response({"message": "Delete Succeed", "code": "200"}, status=status.HTTP_200_OK)
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