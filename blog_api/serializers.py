from django.contrib.auth.models import User
from rest_framework import serializers

from blog.models import Post, Category


# class PostSerializer(serializers.Serializer):
#     # 需要序列化和反序列化的字段列表
#     # allow_blank, allow_null, default, error_messages, format, help_text, initial, input_formats, label, max_length,
#     # min_length, required, read_only, style, source, trim_whitespace, validators, write_only,
#     title = serializers.CharField(max_length=70)
#     body = serializers.CharField()
#     create_time = serializers.DateTimeField()
#     modified_time = serializers.DateTimeField()
#     excerpt = serializers.CharField(max_length=200, allow_blank=True)
#
#     # 定义创建方法
#     def create(self, validated_data):
#         return Post.objects.all(**validated_data)
#
#     # 定义修改方法
#     def update(self, instance, validated_data):
#         instance.title = validated_data.get('title', instance.title)
#         instance.body = validated_data.get('body', instance.body)
#         instance.create_time = validated_data.get('create_time', instance.create_time)
#         instance.modified_time = validated_data.get('modified_time', instance.modified_time)
#         instance.excerpt = validated_data.get('excerpt', instance.excerpt)


class UserSerializer(serializers.ModelSerializer):
    posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'posts']
        filter_fields = ['__all__']


class PostSerializer(serializers.ModelSerializer):
    # author = UserSerializer()
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
