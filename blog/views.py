import markdown
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from blog.forms import PostForm
from blog.models import Post, Category, Tag
from comment.forms import CommentForm
import datetime


# ########################## HomePage ###################################
# def index(request):
#     return HttpResponse("Hello django")


def index(request):
    title = "My Blog Home"
    welcome = "Welcome to My Blog"
    return render(request, 'blog\index_home.html', locals())


def hours_ahead(request, offset):
    try:
        offset = int(offset)
    except ValueError as e:
        print(e)
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    return HttpResponse("{} hours later is {}".format(offset, dt))


def home(request):
    # 获取 Post 模型下的全部数据
    post_list = Post.objects.all()

    # # 函数中创建 Paginator 分页
    # # 创建分页实例对象，第一个参数为列表，第二个参数为每页的列表数量
    # paginator = Paginator(post_list, 10)
    # # 获取分页的页码
    # p = request.GET.get('page')
    # try:
    #     # 获取该分页下的列表内容
    #     post_list = paginator.page(p)
    # except EmptyPage:
    #     # 如果该页为空，则返回最后一页
    #     post_list = paginator.page(paginator.num_pages)
    # except PageNotAnInteger:
    #     # 如果 p 不是整数则返回第一页的内容
    #     post_list = paginator.page(1)

    # 通过 render 将 context 的值更新到模版
    # context 的值可以通过 locals() 方法传递，必须同模版的参数名相同
    return render(request, "blog/index.html", locals())


class HomeView(ListView):
    # 对应的 model
    model = Post
    # 对应的模版
    template_name = 'blog/index.html'
    # 对应的模型列表数据保存的变量名
    context_object_name = 'post_list'
    # 分页，每页数量
    paginate_by = 1

    # 自己创建分页效果
    def get_context_data(self, **kwargs):
        # 获得父类生成的传递给模板的字典
        context = super(HomeView, self).get_context_data(**kwargs)

        # 父类生成的字典中已有 paginator、page_obj、is_paginated 这三个模板变量
        paginator = context.get("paginator")
        page = context.get("page_obj")
        is_paginated = context.get("is_paginated")

        # 获得显示分页导航条需要的数据
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        # 将分页导航条的模板变量更新到 context 中
        context.update(pagination_data)
        return context

    def pagination_data(self, paginator, page, is_paginated):
        # 不需要显示分页返回空字典
        if not is_paginated:
            return {}

        # 当前页左侧的页码
        left = []
        # 当前页右侧的页码
        right = []
        # 标示第一页后是否需要显示省略号
        left_has_more = False
        # 标示最后一页后是否需要显示省略号
        right_has_more = False
        # 是否需要显示第一页的页码号
        first = False
        # 是否需要显示最后一页的页码号
        last = False
        # 当前页的页码
        page_num = page.number
        # 总的页码数
        total_pages = paginator.num_pages
        # 页码的范围
        page_range = paginator.page_range

        # 当前页为首页时候，左侧不存在页码，即为默认，右侧页码根据显示的需求设置
        if page_num == 1:
            right = page_range[page_num: page_num + 1]

            # 如果最右边的页码小于总页数 - 1，即中间存在别的页码，需要显示省略号来显示
            if right[-1] < total_pages - 1:
                right_has_more = True

            # 如果最右边的页码小于总页数，则需要显示最后一页的页码
            if right[-1] < total_pages:
                last = True

        # 如果当前页为最后一页时，右侧不存在页码，即为默认，设置左侧的页码
        elif page_num == total_pages:
            # 如果当前页 - 3 大于 0 则为 page_num - 3 到 page_num - 1 页，否则为 0 到 page_num - 1 页
            left = page_range[(page_num - 2) if (page_num - 2) > 0 else 0: page_num - 1]

            # 如果最左侧的页码大于 2，则之间存在别的号码，需要显示省略号来显示
            if left[0] > 2:
                left_has_more = True

            # 如果最左侧的页码大于 1，则需要显示第一页页码
            if left[0] > 1:
                first = True

        # 其余情况左侧页码为当前页前两页，右侧页码为后两页
        else:
            left = page_range[(page_num - 2) if (page_num - 2) > 0 else 0: page_num - 1]
            right = page_range[page_num: page_num + 1]

            if right[-1] < total_pages - 1:
                right_has_more = True

            if right[-1] < total_pages:
                last = True

            if left[0] > 2:
                left_has_more = True

            if left[0] > 1:
                first = True

        return {'left': left,
                'right': right,
                'first': first,
                'last': last,
                'left_has_more': left_has_more,
                'right_has_more': right_has_more}


# ########################## BlogDetailPage #############################
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # 增加阅读量
    post.increase_views()
    post.body = markdown.markdown(post.body, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ])
    form = CommentForm()
    comment_list = post.comment_set.all()
    return render(request, "blog/detail.html", locals())


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    # 返回一个 HttpResponse 实例，只有当 get 方法被调用后才有 self.object 属性，即 post 实例
    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        # 自增操作，self.object 的值即 post 对象
        self.object.increase_views()
        return response

    # 根据 post 的 pk 值获取相应的 post 实例
    def get_object(self, queryset=None):
        post = super(PostDetailView, self).get_object(queryset=None)
        # 通过获取 post 实例进行相应渲染操作
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ])

        post.body = md.convert(post.body)
        return post

    # 返回一个字典，为模版变量字典，传递给相应的模版
    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update(locals())
        return context


# ########################## ArchivesPage ############################
def archives(request, year):
    post_list = Post.objects.filter(create_time__year=year)
    return render(request, "blog/index.html", locals())


class ArchivesView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    # 获取列表，该方法默认获取指定模型的全部列表数据，通过复写改变默认行为
    def get_queryset(self):
        # 在类视图中，从 URL 捕获的命名组参数值保存在实例的 kwargs 属性（是一个字典）里，
        # 非命名组参数值保存在实例的 args 属性（是一个列表）里
        year = self.kwargs.get('year')
        # 复写，指定筛选的条件，获取相应条件的列表
        return super(ArchivesView, self).get_queryset().filter(create_time__year=year)


# 由于指定的属性同 HomeView，也可以直接继承 HomeView
# 然后复写 get_queryset() 方法改变获取列表的默认行为达到相同效果
class ArchivesView2(HomeView):
    def get_queryset(self):
        year = self.kwargs.get('year')
        return super(ArchivesView2, self).get_queryset().filter(create_time__year=year)


# ########################## CategoryPage ############################
def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate)
    return render(request, "blog/index.html", locals())


class CategoryView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        category = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=category)


# ########################## TagPage ################################
def tags(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    post_list = Post.objects.filter(tags=tag)
    return render(request, 'blog/index.html', locals())


class TagView(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "pot_list"
    paginate_by = 10

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)


def search(request):
    # 获取到用户提交的搜索关键词，字典的键值同模版中的 name 属性值
    q = request.GET.get('q')
    error_message = ''

    # 如果 q 为空则提示输入
    if not q:
        error_message = 'Input Keyword'
        return render(request, 'blog/index.html', locals())

    # Q 对象用于包装查询表达式，其作用是为了提供复杂的查询逻辑
    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'blog/index.html', locals())


def full_posts(request):
    post_list = Post.objects.all()
    return render(request, 'blog/full-width.html', locals())


class FullPostView(HomeView):
    model = Post
    template_name = 'blog/full-width.html'
    context_object_name = 'post_list'
    paginate_by = 10


def about(request):
    return render(request, 'blog/about.html', None)


def contract(request):
    return render(request, 'blog/contact.html', None)


def query(request):
    _q = request.GET.get('_q')
    error_message = ""

    if not _q:
        error_message = 'Input Keyword'
        return render(request, 'blog/full-width.html', locals())

    post_list = Post.objects.filter(Q(title__icontains=_q) | Q(body__icontains=_q))
    return render(request, 'blog/full-width.html', locals())


def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = post.user
            post.save()
            return redirect(post)
    else:
        form = PostForm()
    return render(request, 'blog/post_new.html', locals())
