from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('entradas/',views.entradas_view,name='entradas'),
    path('saidas/',views.saidas_view,name='saidas'),
    path('extrato/',views.extrato_views,name='extrato'),
    path('nav/',views.nav_view,name='nav'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('csv/',views.exportar_csv,name='csv'),
    path('pdf/',views.exportar_pdf,name='pdf'),
]