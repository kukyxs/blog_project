from django.conf.urls import url
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'posts', views.PostViewSet)
router.register(r'post', views.PostViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoryViewSet)

urlpatterns = [
    # url(r'^posts/$', views.post_list, name='api_posts'),
    # url(r'^posts/$', views.post_list_view, name='api_posts'),
    # url(r'^posts/$', views.PostList.as_view(), name='api_posts'),
    # url(r'^posts/$', views.PostListMixin.as_view(), name='api_posts'),
    # url(r'^posts/$', views.PostL.as_view(), name='api_posts'),

    # url(r'^post/(?P<pk>[0-9]+)/$', views.post_detail, name='api_post'),
    # url(r'^post/(?P<pk>[0-9]+)/$', views.post_detail_view, name='api_post'),
    # url(r'^post/(?P<pk>[0-9]+)/$', views.PostDetail.as_view(), name='api_post'),
    # url(r'^post/(?P<pk>[0-9]+)/$', views.PostDetailMixin.as_view(), name='api_post'),
    # url(r'^post/(?P<pk>[0-9]+)/$', views.PostD.as_view(), name='api_post'),

    # url(r'^categories/$', views.categories_view, name='categories'),

    # url(r'^category/(?P<pk>[0-9]+)/$', views.category_detail_view, name='category'),

    url(r'^login/$', obtain_auth_token, name='get_author_token'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
