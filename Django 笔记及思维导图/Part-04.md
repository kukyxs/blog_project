##### 六. Django admin 后台管理系统

1. 在后台管理系统注册创建的模型

   ```python
   from django.contrib import admin
   from blog.models import Post, Category, Tag

   # 在应用目录下的 admin.py 文件中，对创建的模型进行注册，可以一起用列表注册，也可以分开注册
   admin.site.register([Post, Category, Tag])
   ```

   然后运行项目，```python manager.py runserver 192.168.x.xxx:8080```

   可以通过 "http://192.168.x.xxx:8080/admin" 打开 admin 管理系统，可以找到站点管理，对模型进行管理

2. 自定义 admin

   ```python
   # 在使用后台管理的时候，可能需要自己定制 admin 的显示内容，可以通过如下进行定制
   @admin.register(Post)
   class PostAdmin(admin.ModelAdmin)
   	list_display = ['title', 'category', 'author'] # 需要展示的字段
   	
   # 或者通过以下方式注册，效果是一样的
   class PostAdmin(admin.ModelAdmin)
   	list_display = ['title', 'category', 'author'] 
   	
   admin.site.register(Post, PostAdmin)

   @admin.register(Category)
   class CategoryAdmin(admin.ModelAdmin)
       # 显示的标签字段，字段不能是 ManyToManyField 类型
       list_display = ('title', 'publisher')
       
   	# 设置每页显示多少条记录，默认是100条
       list_per_page = 20
       
       # 设置默认可编辑字段
       list_editable = ['title', 'author']
       
       # 排除一些不想被编辑的 fields, 没有在列表的不可被编辑
       fields = ('title', 'author')
       
       # 设置哪些字段可以点击进入编辑界面
       list_display_links = ('tag', 'title')
       
       # 进行数据排序，负号表示降序排序
       ordering = ('-id',)
       
       # 显示过滤器
       list_filter = ('author', 'title')
       
       # 显示搜索框，搜索框大小写敏感
       search_fields = ('title',)
       
       # 详细时间分层筛选
       date_hierarchy = 'create_time'
       
       # 增加多选框 filter_horizaontal 和 filter_vertical 作用相同，只是方向不同，只用于
       # ManyToManyField 类型的字段
       filter_horizontal = ('authors',)
       
   # 修改 admin 页面显示标题
   admin.site.site_header = "Blog Manager System"
   # 修改 admin 页面头部标题
   admin.site.site_title = "Blog Manager"
   ```

##### 七. Django 表单

###### 存在相应模型（POST 方式）

1. 在应用文件夹下创建 forms.py 文件存放表单

   ```python
   from django import forms
   from .models import Post

   # 表单类必须继承 forms.ModelForm 或者 forms.Form 类，如果有相应的模型，则使用 ModelForm 更方便
   class PostForm(forms.ModelForm):
       class Meta:
           # 表单对应的数据库模型
           model = Post
           # 指定表单需要显示的字段
           fields = ['title', 'body']
   ```

2. 创建表单视图

   ```python
   from django.shortcuts import render, redict
   from blog.models import Post
   from blog.forms import PostForm

   def new_post(request):
       # Http 请求包括 POST 和 GET 两种，一般提交数据都是用 POST 请求
       # 因此当 request.method 为 POST 的时候才需要处理表单数据
       if request.method = 'POST':
           # 用户提交的信息存在 request.POST 中，相当于一个字典取值
           form = PostForm(request.POST)
           # 判断表单是否有效，Django 自动校验表单数据是否合理，根据模型的字段类型来判断
           if form.is_valid():
               # commit=False 表示只生成模型类的实例，不马上保存到数据库
               post = form.save(commit=Flase)
               # 将作者和文章进行关联
               post.author = request.user
               # 通过调用 save() 方法将数据存入数据库
               post.save()
               # return render('post_detail', pk=post.pk)
               # 如果模型类中定义了 get_absolute_url 方法，可以用以下方式跳转
               # 会直接跳转 get_absolute_url 方法所指向的地址
               return redirect(post)
   	else:
           # 如果不是 POST 重定向到空白的新建页面
           form = PostForm()
   	return render(request, 'blog/post_new.html', locals())
   ```

3. 绑定 URL

   ```python
   urlpatterns = [url(r'^post/new/$', views.new_post, name='new_post'),]
   ```

4. 通过模版进行表单的前端渲染

   ```html
   <form action="{% url 'blog:new_post' %}" method="post" >
       {# 防止被攻击，使表单更加安全 #}
       {% csrf_token %}
       <div class="row">
           <div class="col-md-12">
               <label for="{{ form.title.id_for_label }}">标题：</label>
               {# 根据模型的字段类型自动渲染成表单 #}
               {{ form.title }}
               {# 渲染表单对应的错误 #}
               {{ form.title.errors }}
           </div>
           
           <div class="col-md-12">
               <label for="{{ form.text.id_for_label }}">标题：</label>
               {{ form.text }}
               {{ form.text.errors }}
           </div>
           
           <div>
               <button type="submit" class="submit-btn">发表：</button>
           </div>
       </div>
   </form>
   ```

###### 不存在对应模型（POST 方式）

1. 在 forms.py 中创建表单

   ```python
   # 假设有个信息反馈的表单
   class ContractForm(forms.Form):
       subject = forms.CharField(max_length=100)
       email = forms.EmailField(required=False, label='Your Email')
       message = forms.CharField(widget=forms.Textarea(attrs={'clos': 80, 'rows': 20}))
       
       # 自定义校验规则，以 clean 开头，字段名结尾，校验时候自动调用方法
       # 例如过滤信息长度小于 4 个字的信息，提示用户修改
   	def clean_message(self):
           message = self.cleaned_data['message']
           num_word = len(self.message.split())
           if num_word < 4:
               raise forms.ValidationError('Not Enough words')
           return message
   ```

2. 创建表单视图

   ```python
   def post_contract(request):
   	if request.method = 'POST':
           form = ContractForm(request.POST)
           if form.is_valid():
               # 只打印查看提交的结果是否正确
               cd = form.cleaned_data
               print(cd)
               # 提交成功后跳转 home 页面，通过 spacename 和 name 值指定页面
               return redict('blog:home')
       else:
           # 不是 POST 方式则重定向到空白页面
           form = ContractForm()
   	return render(request, 'blog/contact_post.html', locals())
   ```

3. 绑定 URL

   ```python
   urlpatterns = [url(r'^contract/$', 'contract_us.html', name='contract_us'),]
   ```

4. 通过模版进行表单的前端渲染

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <title>Contact us</title>
   </head>

   <body>
   <h1>Contact Us</h1>
       
   {% if form.errors %}
       <p style="color: red;">
           Please correct the error{{ form.errors|pluralize }} below.
       </p>
   {% endif %}

   <form action="" , method="post">
       {% csrf_token %}
       <table>
           {{ form.as_table }}
       </table>
       <input type="submit" value="Submit">
   </form>
   </body>
   </html>
   ```

###### 类似搜索的表单（GET）

1. 创建表单视图

   ```python
   def search(request):
       # 获取到用户提交的搜索关键词，字典的键值同模版中的 name 属性值
       q = request.GET.get('q')
       error_message = ''
   	# 根据 q 的值是否空设置相关信息
       if not q:
           error_message = 'Input Keyword'
           return render(request, 'blog/home.html', locals())

       # Q 对象用于包装查询表达式，其作用是为了提供复杂的查询逻辑
       post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
       return render(request, 'blog/home.html', locals())
   ```

2. 绑定 URL

   ```
   urlpatterns = [url(r'^search/$', views.search, name='search'),]
   ```

3. 通过模版进行表单的前端渲染

   ```html
   {# ...... #}
   <div id="search-form" class="search-form">
   	<form role="search" method="get" id="searchform" action="{% url 'blog:search' %}">
   		<input type="search" name="q" placeholder="搜索" required>
   		<button type="submit"><span class="ion-ios-search-strong"></span></button>
   	</form>
   </div>
   {# ...... #}
   ```