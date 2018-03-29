import markdown
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        # 指定表名为 category，默认为 blog-category
        db_table = "category"


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "tag"


class Post(models.Model):
    title = models.CharField(max_length=70)
    body = models.TextField()
    create_time = models.DateTimeField()
    modified_time = models.DateTimeField()
    excerpt = models.CharField(max_length=200, blank=True)

    # 加上 on_delete 属性，否则可能报错
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # reverse 会自动指向 'blog:post_detail' 所指向的 url，kwargs 为传入的参数值
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def increase_views(self):
        self.views += 1
        # 指定更新字段，提高更新的效率
        self.save(update_fields=['views', ])

    def save(self, *args, **kwargs):
        if not self.excerpt:
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # strip_tags 作用是去除文本中的 html 标签
            self.excerpt = strip_tags(md.convert(self.body))[:50]
        super(Post, self).save(*args, **kwargs)

    class Meta:
        db_table = "post"
        # 排序方式 - 为按照字段逆序
        ordering = ['-create_time']
