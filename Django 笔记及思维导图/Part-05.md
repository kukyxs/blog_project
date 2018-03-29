##### 八. 利用 Django 通用视图类创建类视图

1. 创建视图类

   ``````python
   import markdown
   from django.shortcuts import render
   from django.views.generic import ListView, DetailView
   from django.shortcuts import get_object_or_404
   from blog.models import Post

   # 获取相应模型下的全部数据
   def home(request):
       post_list = Post.objects.all()
       return render(request, 'blog/home.html', locals())

   # 通过 ListView 类来进行修改
   class HomeView(ListView):
       model = Post # 指定视图模型
       template_name = 'blog/home.html' # 指定渲染的模版
       context_objects_name = 'post_list' # 对应的模型列表数据保存的变量名

   # #################################################################################
   # 获取特定条件下的模型数据 
   def category(request, pk):
       category = get_object_or_404(Category, pk=pk)
       post_list = Post.objects.filter(category=category)
       return render(request, 'blog/home.html', locals())

   # 通过 ListView 类进行修改
   # 基本属性同 HomeView 相同，也可以直接继承 HomeView 然后复写 get_queryset() 方法实现
   class CategoryView(ListView):
       model = Post
       template_name = 'blog/home.html'
       context_objects_name = 'post_list'
       
       # 该方法默认返回指定模型的全部数据，通过复写该方法，改变默认行为
       def get_queryset(self):
           # 类视图中，从 url 捕获的命名组参数值保存在实例的 kwargs 中，是一个字典
           # 非命名组参数值保存在实例的 args 中，是一个列表
           category = get_object_or_404(Category, pk=kwargs.get('pk'))
           return super(CategoryView, self).get_queryset().filter(category=category)

   # #################################################################################
   # 获取具体的详情
   def post_detail(request, pk):
       post = get_object_or_404(Post, pk=pk)
       post.increase_views()
       post.body = markdown.markdown(post.body, extensions=[
           'markdown.extensions.extra',
           'markdown.extensions.codehilite',
       ])
       form = CommentForm()
       return render(request, 'blog/detail.html', locals())

   class PostDetailView(DetailView):
       model = Post
       template_name = 'blog/detail.html'
       context_objects_name = 'post'
       
       # 方法返回一个 HttpResponse 实例
       def get(self, request, *args, **kwargs):
           # get 方法会通过调用 get_object 和 get_context——data 方法对模版渲染
           # def get(self, request, *args, **kwargs):
           	# self.object = self.get_object()
           	# context = self.get_context_data(object=self.object)
           	# return self.render_to_response(context)
           response = super(PostDetailView, self).get(request, *args, **kwargs)
           # 只有当 get 方法被调用后才有 self.object 属性，即 post 实例
           # 对应 post_detail 函数中的 post.increase_views()
           self.object.increase_views()
           return response
       
       # 根据 post 的 pk 值获取相应的 post 实例
       def get_object(self, queryset=None):
           post = super(PostDetailView, self).get_object(queryset=None)
           post.body = markdown.markdown(post.body, extensions=[
           	'markdown.extensions.extra',
           	'markdown.extensions.codehilite',
       	])
           return post
       
       # 返回一个字典，为模版变量字典，传递给相应的模版
       def get_context(self, **kwargs):
           context = super(PostDetailView, self).get_context(**kwargs)
           form = CommentForm()
           # 更新 context 的内容，必须调用
           context.update(locals())
           return context
   ``````

2. 绑定 url

   ``````python
   urlpatterns = [
   	# url(r'^home/$', views.home, name='home'),
   	url(r'^home/$', views.HomeView.as_view(), name='home'),
   	# url(r'cate/(?P<pk>[0-9]+)/$', views.category, name='cate'),
   	url(r'cate/(?P<pk>[0-9]+)/$', views.CategoryView.as_view(), name='cate'),
   	# url(r'post/(?P<pk>[0-9]+)/$', views.post_detail, name='post'),
   	url(r'post/(?P<pk>[0-9]+)/$', views.PostDetailView.as_view(), name='post'),
   ]
   ``````

#####九. 创建分页

######通过 ListView 创建分页

1. 指定 ListView 中的 paginate_by 属性来设置分页

   ``````python
   class PostListView(ListView):
       model = Post
       template_name = 'blog/home.html'
       context_objects_name = 'post_list'
       # 指定分页，每页数量为 10
       paginate_by = 10
   ``````

2. 在模版中加入分页

   ``````html
   {# ...... #}
   {% if is_paginated %}
   	<div class="pagination-simple">
   		{% if page_obj.has_previous %}
   			<a href="?page={{ page_obj.previous_page_number }}">Previous</a>
   		{% endif %}
   			<span class="current">
                    Page {{ post_list.number }} of {{ post_list.paginator.num_pages }}
           	</span>
           {% if page_obj.has_next %}
           	<a href="?page={{ page_obj.next_page_number }}">Next</a>
           {% endif %}
   	</div>
   {# ...... #}
   ``````

###### 通过 Paginator 创建分页

1. 创建相应的视图

   ``````python
   def home(request):
       limit = 10
       posts = Post.object.all()
       paginator = Paginator(posts, limit)
       
       # 根据表单获取页码
       page = request.GET.get('page')
       try:
           post_list = paginator.page(page) # 获取 num 页码下的列表
       except PageNotAnInteger:
           post_list = paginator.page(1) # 如果 page 不是整数则返回第一页列表
   	except EmptyPage:
           post_list = paginator.page(paginator.num_pages) # 如果没有数据则返回最后一页列表
   	
       return render(request, 'blog/home.html', locals())
   ``````

2. 通过模版进行渲染

   ``````html
   {% for post in post_list %}
       {{ post.title }}<br />
       ...
   {% endfor %}

   <div class="pagination">
       <span class="step-links">
           {% if post_list.has_previous %}
               <a href="?page={{ post_list.previous_page_number }}">previous</a>
           {% endif %}
           
           <span class="current">
               Page {{ post_list.number }} of {{ post_list.paginator.num_pages }}
           </span>

           {% if post_list.has_next %}
               <a href="?page={{ post_list.next_page_number }}">next</a>
           {% endif %}
       </span>
   </div>
   ``````



> Paginator 常用属性
>
> ``````python
> from django.core.paginator import Paginator
>
> item_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']
> # 指定 paginator 的列表以及每页显示的列表数量
> p = Paginator(item_list, 2)
> print(p.count) # 返回列表的总数	14
> print(p.num_pages) # 返回总页数    7
> print(p.page_range) # 返回页数的范围	(1, 8)
> print(p.per_page) # 返回每页列表的数量
> print(p.object_list) # 返回所有的列表 item
>
> # 通过 page(num) 方法获取 num 页的列表 <Page 2 of 7>
> page2 = p.page(2)
> print(page2.number) # 获取当前页的页码
> print(page2.object_list) # 获取该页码下的所有列表    ['c', 'd']
> print(page2.has_next()) # 是否有下页    True
> print(page2.has_previous()) # 是否有上页    True
> print(page2.has_other_pages()) # 是否有其他页    True
> # 如果没有上/下一页则返回 EmptyPage 错误 EmptyPage: That page contains no results
> print(page2.next_page_number()) # 获取下一页的页码    3
> print(page2.previous_page_number()) # 获取上一页的页码    1
> print(page2.start_index()) # 当前页第一个 item 在列表中的位置    3
> print(page2.end_index()) # 当前页最后一个 item 在列表中的位置    4
> ``````

