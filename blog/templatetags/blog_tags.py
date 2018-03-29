from django import template
from django.db.models import Count, Avg

from blog.models import Post, Category, Tag

register = template.Library()


@register.simple_tag
def get_recent_posts(num=5):
    return Post.objects.all().order_by("-create_time")[:num]


@register.simple_tag
def archives():
    return Post.objects.dates('create_time', 'year', order='DESC')


@register.simple_tag
def get_all_category():
    # 通过 annotate 获得该分类下的文章总数
    # annotate 类似于 all 的功能，同时额外统计了 post 的数量，字段名为 num_post，可直接通过 category 实例调用 num_post 字段
    # annotate 还可以连接 Avg, Max, Min 等
    # 例如 Goods 模型下有 price 字段
    # Goods.objects.annotate(avg_price=Avg('price')) 求平均，可以直接调用 avg_price 字段
    # Goods.objects.annotate(max_price=Max('price)) 求最大值
    return Category.objects.annotate(num_post=Count('post')).filter(num_post__gt=0)


@register.simple_tag
def get_all_tag():
    return Tag.objects.annotate(num_post=Count('post')).filter(num_post__gt=0)
