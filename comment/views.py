from django.shortcuts import render, get_object_or_404, redirect

from blog.models import Post
from comment.forms import CommentForm, ContractForm


def post_comment(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect(post)

        else:
            comment_list = post.comment_set.all()
            return render(request, 'blog/detail.html', locals())

    return redirect(post)


def post_email(request):
    if request.method == 'POST':

        form = ContractForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            print(cd)
            return redirect('blog:home')
    else:
        form = ContractForm()

    return render(request, 'comment/contract_form.html', locals())
