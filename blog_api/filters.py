import django_filters

from blog.models import Post


class PostFilter(django_filters.rest_framework.FilterSet):
    # 指定筛选参数的筛选条件
    title = django_filters.CharFilter("title", lookup_expr='icontains')

    # 指定筛选的 model 和 参数
    class Meta:
        model = Post
        fields = ['title']
