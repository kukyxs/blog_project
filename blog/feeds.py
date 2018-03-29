from django.contrib.syndication.views import Feed
from .models import Post


# Rss
class AllPostFeed(Feed):
    title = "Django blog 测试项目"

    link = '/'

    description = "Django blog 测试项目"

    def items(self):
        return Post.objects.all()

    def item_title(self, item):
        return '[{}] {}'.format(item.category, item.title)

    def item_description(self, item):
        return item.body
