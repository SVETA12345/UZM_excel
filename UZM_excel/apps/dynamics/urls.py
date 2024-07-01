from django.urls import path
from . import views

urlpatterns = [
    path('', views.dynamics_traj, name='dynamics'),
    path('edit', views.edit_dynamics_traj, name='edit_dynamics'),
    path('meas_del', views.del_dynamics)
]
