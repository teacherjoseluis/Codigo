from django.urls import path

from restaurante.api import views


app_name = 'api'

urlpatterns = [
    path('health/', views.HealthAPIView.as_view(), name='health'),
    path(
        'sucursales/',
        views.SucursalSistemaListAPIView.as_view(),
        name='sucursal-list',
    ),
    path(
        'sucursales/<int:pk>/',
        views.SucursalSistemaDetailAPIView.as_view(),
        name='sucursal-detail',
    ),
    path(
        'catalogos/clasificaciones/',
        views.CatalogoClasificacionListAPIView.as_view(),
        name='catalogo-clasificacion-list',
    ),
    path(
        'catalogos/unidades-medida/',
        views.UnidadMedidaListAPIView.as_view(),
        name='unidad-medida-list',
    ),
    path(
        'catalogos/presentaciones/',
        views.PresentacionListAPIView.as_view(),
        name='presentacion-list',
    ),
    path(
        'catalogos/tipos-cuenta-contable/',
        views.TipoCuentaContableListAPIView.as_view(),
        name='tipo-cuenta-contable-list',
    ),
]
