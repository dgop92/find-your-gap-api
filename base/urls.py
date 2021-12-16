from django.conf.urls import url

from base import views

results_view_name = "results"
register_view_name = "register"
analyze_view_name = "analyze"
automatic_register_view_name = "automatic"

urlpatterns = [
    url(r"results", views.results_view, name=results_view_name),
    url(r"register", views.register_view, name=register_view_name),
    url(r"analyze", views.analyze_meeting_view, name=analyze_view_name),
    url(
        r"automatic",
        views.automatic_register_view,
        name=automatic_register_view_name,
    ),
    url(
        r"^users/(?P<username>[\w]+)$",
        views.UninorteUserDetail.as_view(),
        name=views.UninorteUserDetail.name,
    ),
]
