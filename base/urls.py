from django.conf.urls import url
from base import views

results_view_name = "results"
register_view_name = "register"

urlpatterns = [
    url(r'results', views.results_view, name = results_view_name),
    url(r'register', views.register_view, name = register_view_name),
    url(r'^users/(?P<username>[\w]+)$', 
        views.UninorteUserDetail.as_view(), 
        name = views.UninorteUserDetail.name
    )
]