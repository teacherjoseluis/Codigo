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
    path(
        'registros-maestro/',
        views.RegistroMaestroListCreateAPIView.as_view(),
        name='registro-maestro-list',
    ),
    path(
        'registros-maestro/<int:pk>/',
        views.RegistroMaestroDetailAPIView.as_view(),
        name='registro-maestro-detail',
    ),
    path(
        'registros-maestro/<int:pk>/disable/',
        views.RegistroMaestroDisableAPIView.as_view(),
        name='registro-maestro-disable',
    ),
    path(
        'registros-maestro/<int:pk>/compra/',
        views.RegistroMaestroCompraAPIView.as_view(),
        name='registro-maestro-compra',
    ),
    path(
        'registros-maestro/<int:pk>/venta/',
        views.RegistroMaestroVentaAPIView.as_view(),
        name='registro-maestro-venta',
    ),
    path(
        'registros-maestro/<int:pk>/inventario/',
        views.RegistroMaestroInventarioAPIView.as_view(),
        name='registro-maestro-inventario',
    ),
    path(
        'registros-maestro/<int:pk>/contabilidad/',
        views.RegistroMaestroContabilidadAPIView.as_view(),
        name='registro-maestro-contabilidad',
    ),
    path(
        'registros-maestro/<int:pk>/pedimento/',
        views.RegistroMaestroPedimentoAPIView.as_view(),
        name='registro-maestro-pedimento',
    ),
    path(
        'registros-maestro/<int:pk>/foto/',
        views.RegistroMaestroFotoAPIView.as_view(),
        name='registro-maestro-foto',
    ),
    path(
        'registros-maestro/<int:pk>/ubicaciones/<int:ubicacion_id>/',
        views.RegistroMaestroUbicacionFisicaAPIView.as_view(),
        name='registro-maestro-ubicacion',
    ),
]
