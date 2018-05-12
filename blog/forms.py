from django import forms
from .models import Post


# 表单类必须继承 forms.ModelForm 或者 forms.Form 类，如果有相应的模型，则使用 ModelForm 更方便
class PostForm(forms.ModelForm):
    class Meta:
        # 表单对应的数据库模型
        model = Post
        # 指定表单需要显示的字段
        fields = ['title', 'body']
