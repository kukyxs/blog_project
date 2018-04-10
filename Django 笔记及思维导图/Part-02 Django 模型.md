上一部分我们介绍了环境和项目的搭建，以及数据库的配置，那这一部分我们介绍和数据库相关方面的知识 -- 模型

###### 创建 django 模型
我们需要在 "blog" 应用下的 models.py 文件中添加 django 数据库模型，模型类需要继承 models.Model 类，例如
```python
from django.db import models
class Category(models.Model):
	# 可以通过第一个参数传入字符串设置别名
	name = models.CharField("分类", max_length=100)

	# 查找 Category 时，返回为一个 object 如果不重写 __str__ 方法返回数据直接显示 Category Object，
	# 重写该方法后，查找返回结果为该方法返回的值
	def __str__(self):
		return '<Category>[{}]'.format(self.name)
		
	# 通过 Meta 来修改数据表的信息
	class Meta:
		db_table = "category" # 修改数据库表名，默认表名会是 项目名_模型名 blog_category
		ordering =  ['-id'] # 修改排序方式，"-" 表示逆序
```
Model 的常用字段类型还是比较多的，下面将介绍常用的字段类型和关系类型，以及字段类型的限制参数。
###### Model 的常用字段类型
> 1. models.AutoField 	自增列	如果没有的话，默认会生成一个名称为 id 的列，如果要显示的自定义一个自增列，必须将给列设置为主键 primary_key=True
> 2. models.CharField　　字符串　　指定 max_length 参数设置最大长度
> 3. models.BooleanField　　布尔类型
> 4. models.DateField　　日期类型        对于参数，auto_now = True 则每次更新都会更新这个时间，auto_now_add 则只是第一次创建添加，之后的更新不再改变
> 5. models.DateTimeField　　日期类型       同 models.DateField
> 6. models.EmailField　　字符串类型（正则表达式邮箱）
> 7. models.FloatField　　浮点类型
> 8. models.IntegerField　　整型
> 9. models.BigIntegerField　　长整型
> 10. models.IPAddressField　　字符串类型（ip4正则表达式）
> 11. models.GenericIPAddressField　　字符串类型（ip4和ip6是可选的）    参数protocol可以是：both、ipv4、ipv6
> 12. models.TextField　　字符串类型    同 CharField， 可以设置更长的字符串
> 13. models.TimeField　　时间 HH:MM[:ss[.uuuuuu]]
> 14. models.URLField　　字符串，地址正则表达式
> 15. models.ImageField     图片类型
> 16. models.FilePathField    文件类型

###### Model 的连表结构

> 1. 一对多:models.ForeignKey(其他表)        例如 ModelA 中有个字段指向 ModelB  
>    ```python
>    # 最好加上 on_delete 属性, 否则可能会报错
>    b = models.ForeignKey(ModelB，on_delete=models.CASCAED)
>    ```
>    ModelA 为”多“，ModelB 为”一“
>
> 2. 多对多:models.ManyToManyField(其他表)        例如 ModelA 中有个字段指向 ModelB 
>    ```python
>    bs = models.ManyToManyField(ModelB)
>    ```
>    ModelA 可以对应多个 ModelB 的值，同样 ModelB 可以对应多个 ModelA 的值
>
> 3. 一对一:models.OneToOneField(其他表)        例如 ModelA 中有字段指向 ModelB
>    ```python
>    b = models.OneToOneField(ModelB)
>    ```
>    ModelA 只能对应 ModelB 中特定的值，同样 ModelB 也只能对应 ModelA 中特定的值

###### Model 的常用设置参数
> 1. null=(True/False)        数据库中字段是否可以为空
> 2. blank=(True/False)        django的 Admin 中添加数据时是否可允许空值
> 3. primary_key=(True/False)        主键，对 AutoField 设置主键后，就会代替原来的自增 id 列
> 4. auto_now=(True/False)        自动创建---无论添加或修改，都是当前操作的时间，在 MySql 下存在过滤月份时候数据为空，解决方案参考 [MySql 文档 Section 10.6](https://dev.mysql.com/doc/refman/5.5/en/time-zone-support.html)
> 5. auto_now_add=(True/False)        自动创建---永远是创建时的时间
> 6. choices=(xx,xx,xx)        可选择列表项，通常是一个列表或者元组
> 7. max_length=(int)        最大长度，多和字符串类型配合使用
> 8. verbose_name='xxxx'        Admin 中字段的显示名称
> 9. name|db_column        数据库中的字段名称
> 10. unique=(True/False)        是否可以重复
> 11. db_index=(True/False)        是否设置为索引
> 12. editable=(True/False)        在Admin里是否可编辑
> 13. error_messages='xxxx'        错误提示
> 14. auto_created=(True/False)        是否自动创建
> 15. help_text='xxxx'        在 Admin 中提示帮助信息
> 16. upload-to='xxxx'        上传到哪个位置，与 ImageField,FfileField 配合使用

创建完模型后，我们需要根据模型来创建数据库，设计到数据库迁移的知识
###### 数据库的迁移
我们通过命令行切换到 manage.py 文件夹，分别运行如下命令行
1. ```python manage.py makemigrations``` 运行后会在相应应用下的 migrations 目录生成一个 0001_initial.py（0001会根据迁移的次数进行递增），用于记录对模型的修改
2. ```python manage.py migrate``` 运行后将 model 中的操作转换成为数据库语言，作用于数据库，对数据库进行相应的修改
如果对命令行做了什么动作，我们可以通过运行如下命令行查看具体的数据库操作```python manage.py sqlmigrate blog 0001``` 其中 blog 0001 根据实际项目进行替换

###### 数据库插入数据

创建好数据库进行数据添加，可以通过如下操作进行
 ```python
from blog.models import Category, Tag
c = Category('test category')
c.save()
t = Tag('test tag')
t.save()
 ```
打开数据库可以看到插入的数据

###### 数据库查找数据

插入数据后，查找数据库内的数据可以通过如下操作进行
```python
# 查找某个表所有的数据，返回<QuerySet[...]>
from blog.models import Category
c_list = Category.objects.all()
# 查找某个特定的数据，如果数据不存在会抛出错误 blog.models.DoesNotExist，
# 存在则返回 Object，如果重写了 __str__ 方法，则返回该方法所指定的值
c_test = Category.objects.get(name='test category')
# 也可以通过 filter 关键词进行查找
c_test = Category.objects.filter(name='test category, id__lt=10)
c_test = Category.objects.filter(id__range=[0, 10])
# 还可以使用 startswith，istartswith, endswith, iendswith 等条件
# .values() 和 .values_list() 区别
# .values() 取出某一列，每个元素是一个字典，.values_list() 取出的元素是一个个元组
# 如下语句得到的结果为 <QuerySet [{'name': 'test category', 'id': 1}]>
print(Category.objects.filter(name='test category').values('name', 'id')) 
# 如下语句得到的结果为 <QuerySet [('test category', 1)]>
print(Category.objects.filter(name='test category').values_list('name', 'id'))
# exclude 查询条件外的数据
Category.objects.exclude(id__gt=2)   即查找 id 不大于 2 的数据
# 通过 order_by 进行排序
Category.objects.all().order_by('-id') # 逆序排序，逆序排序只需要在排序字段前加"-"号即可
# 删选某个范围内的数据 类似于 SQL 语句中的 OFFSET 10 LIMIT 10
Category.objects.all()[10: 20] # 获取列表中 10-20 的数据
# aggregate 操作符(出了求和 Count 还有 Avg, Max, Min 等，通过 django.db.models 导入)
print(Category.objects.aggregate(Count('name')))    # {'name__count': 5}
# 也可以指定结合后的字段名
print(Category.objects.aggregate(category_count=Count('name)))	# {'category_count': 5}
# annotate 操作符
# 假设 Post 表中有个字段指向 Category
# category = models.ForeignKey(Category) 在表 Category 中需要统计某个 category 下 post 数量，
# 但是表 Category 中没有 post_count 字段，那么可以通过 annotate 操作符来进行统计
c_list = Category.objects.annotate(post_count=Count('post'))
print(c_list[0].post_count) # 12
# "__" 的操作
# 大于，小于操作
Categroy.objects.fileter(id__gt=1, id__lt=10) # 查找 id 介于 1 和 10 之间的数据
# in
Category.objects.filter(id__in=[11, 22, 33]) # 查找 id 为 11，22，33 的值
Category.objects.exclude(id__in=[11, 22, 33]) # not in
# contains
Category.objects.filter(name__contains="test") 查找 name 字段包含 test 的值
Category.objects.filter(name__icontains="test") # 大小写不敏感
# range
Caregory.objects.filter(id__range=[1, 10]) # 查找 id 介于 1 和 10 之间的数据，即 between and
# 类似的包括 startwith, istartwith, endwith, iendwith 等
```
###### 数据库修改数据
对存在的数据进行修改，可通过如下操作进行
```python
c = Category.objects.get(name='test category')
c.name = 'new test category'
c.save()
```
###### 删除数据库数据
对存在数据库中的数据进行删除，可以通过如下操作进行
```python
# 删除某条特定的数据
c = Category.objects.get(name='new test category')
c.delete()
# 删除全部的数据
c_list = Category.objects.get()
for c in c_list:
	c.delete()
```
更多的数据库操作 API 查看官方的 API [django 数据库操作 API](https://docs.djangoproject.com/en/1.10/ref/models/querysets/)
###### 使用原生 SQL 语句操作数据库
django 支持使用原生语句操作数据库
```python
from django.db import connection
cursor = connection.cursor()
# 原生 SQL 语句放在 execute 中使用
cursor.execute("SELECT c.id, c.name FROM blog_category as c")
# 获取查询到的第一个数据
row = cursor.fetchone()
# 获取全部查询到的数据
rows = cursor.fetchall()
```
最后项目地址：[blog_project](https://github.com/kukyxs/blog_project)