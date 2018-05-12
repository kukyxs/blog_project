from django.conf.urls import url

from blog.feeds import AllPostFeed
from . import views

app_name = 'blog'
urlpatterns = [
    # url(r'^home$', views.home, name='home'),
    # url(r'^home/$', views.index, name='home'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),

    url(r'^ahead/(?P<offset>\d+)/$', views.hours_ahead, name='time'),

    # url(r'^post/(?P<pk>[0-9]+)/$', views.detail, name="detail"),
    url(r'^post/(?P<pk>[0-9]+)/$', views.PostDetailView.as_view(), name="detail"),

    # url(r'^archives/(?P<year>[0-9]{4})/$', views.archives, name="archives"),
    # url(r'^archives/(?P<year>[0-9]{4})/$', views.ArchivesView.as_view(), name="archives"),
    url(r'^archives/(?P<year>[0-9]{4})/$', views.ArchivesView2.as_view(), name="archives"),

    # url(r'^category/(?P<pk>[0-9]+)/$', views.category, name="category"),
    url(r'^category/(?P<pk>[0-9]+)/$', views.CategoryView.as_view(), name='category'),

    url(r'^tag/(?P<pk>[0-9]+)/$', views.tags, name='tags'),
    # url(r'^tag/(?P<pk>[0-9]+)/$', views.TagView.as_view(), name='tags'),

    url(r'^post/new/$', views.new_post, name='new_post'),

    url(r'^search/$', views.search, name='search'),

    # rss url
    url(r'^all/rss/$', AllPostFeed(), name='rss'),

    url(r'^full/$', views.FullPostView.as_view(), name='full'),

    url(r'^about/$', views.about, name='about'),

    url(r'^contact/$', views.contract, name='contact'),

    url(r'^query/$', views.query, name='query'),
]
