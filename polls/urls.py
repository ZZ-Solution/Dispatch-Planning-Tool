from django.conf.urls import url

from .import views

urlpatterns = [
    # ex: /polls/
	url(r'^$', views.index, name='index'),
    # ex: /polls/5/
	# url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    # ex: /polls/5/results/
	# url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
	# url(r'^submit', views.submit, name="submit"),
	url(r'^hello/?$', views.hello, name = 'hello')
	# url(r'^hello/?$', 'polls.views.hello')
]