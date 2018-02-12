from django.conf.urls import url

from pks import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^lookup$', views.lookup, name='lookup'),
    url(r'^add$', views.add, name='add'),
]
