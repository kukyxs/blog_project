from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.models import Post, Category
from blog_api.filters import PostFilter
from blog_api.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from blog_api.serializers import PostSerializer, CategorySerializer, UserSerializer


@csrf_exempt
def post_list(request):
    # 如果是 GET 请求则返回所有的列表
    if request.method == "GET":
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)

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


@api_view(['GET', 'POST'])
def post_list_view(request, format=None):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostList(APIView):
    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListMixin(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(self, request, *args, **kwargs)


class PostL(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    # 指定筛选参数
    # filter_fields = ['title']
    # 指定筛选类
    filter_class = PostFilter
    authentication_classes = (TokenAuthentication,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post is not None:
            post.delete()
            return Response({"message": "delete succeed", "code": "200"}, status=status.HTTP_200_OK)
        return super(PostViewSet, self).destroy(self, request, *args, **kwargs)


# #############################################################################################################
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
        return JsonResponse(serializer.data, status=200)

    # 如果 request 是 PUT 方法，则解析 request 中的参数，
    # 进行校验是否合理，合理则更新，否则返回 400 BAD REQUEST
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = PostSerializer(post, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    # 如果 request 是 DELETE 方法，则直接删除
    elif request.method == 'DELETE':
        post.delete()
        return HttpResponse(status=204)


@api_view(['GET', 'PUT', 'DELETE'])
def post_detail_view(request, pk, format=None):
    post = get_object_or_404(Post, pk=pk)

    if post is None:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostDetail(APIView):
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk, format=None):
        serializer = PostSerializer(self.get_object(pk=pk))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        serializer = PostSerializer(self.get_object(pk=pk), data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        self.get_object(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class PostD(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


# #############################################################################################################
@api_view(['GET', 'POST'])
def categories_view(request, format=None):
    if request.method == 'GET':
        category_list = Category.objects.all()
        serializer = CategorySerializer(category_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def category_detail_view(request, pk, format=None):
    category = get_object_or_404(Category, pk=pk)

    if category is None:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        category.delete()
        return Response({"code": 200, "message": "delete succeed"}, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        if category is not None:
            category.delete()
            return Response({"message": "delete succeed"})
        return super(CategoryViewSet, self).destroy(self, request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['username', ]
