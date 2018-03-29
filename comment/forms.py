from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'url', 'text']


class ContractForm(forms.Form):
    subject = forms.CharField(max_length=100)
    email = forms.EmailField(required=False, label="Your email")
    message = forms.CharField(widget=forms.Textarea(attrs={'clos': 80, 'rows': 20}))

    # 自定义校验规则，以 clean 开头，字段名结尾，校验时候自动调用
    def clean_message(self):
        message = self.cleaned_data['message']
        num_words = len(message.split())
        if num_words < 4:
            raise forms.ValidationError('Not Enough words')
        return message
