from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='data_info'),
    path('plan', views.plan, name='plan'),
    path('parametrs', views.param, name='param'),
    path('trajectories', views.traj, name='traj'),
    path('edit_trajectories', views.edit_traj, name='edit_traj'),
    path('projection', views.proj, name='proj'),
    path('dynamics/', include('dynamics.urls')),
    path('run_p', views.run_param, name='run_param'),

]
