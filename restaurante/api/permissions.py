from rest_framework.exceptions import PermissionDenied

from restaurante.models import AuthUser_Sucursal, AuthUser_UbicacionFisica


def scoped_sucursal_ids(user):
    if not user or not user.is_authenticated or user.is_superuser:
        return None

    return list(
        AuthUser_Sucursal.objects.filter(user=user.id).values_list(
            'sucursal',
            flat=True,
        )
    )


def scoped_ubicacion_ids(user):
    if not user or not user.is_authenticated or user.is_superuser:
        return None

    return list(
        AuthUser_UbicacionFisica.objects.filter(user=user.id).values_list(
            'ubicacionfisica',
            flat=True,
        )
    )


class SucursalScopedQuerysetMixin:
    sucursal_scope_field = 'id'

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        sucursal_ids = scoped_sucursal_ids(self.request.user)
        if sucursal_ids is None:
            return queryset
        return queryset.filter(**{'{0}__in'.format(self.sucursal_scope_field): sucursal_ids})


def require_ubicacion_scope(user, ubicacion_ids):
    requested_ids = {value for value in ubicacion_ids if value is not None}
    if not requested_ids or not user or not user.is_authenticated or user.is_superuser:
        return

    allowed_ids = scoped_ubicacion_ids(user)
    if allowed_ids is None:
        return
    if not allowed_ids:
        raise PermissionDenied('User has no assigned ubicacion scope.')

    missing_ids = requested_ids.difference(allowed_ids)
    if missing_ids:
        raise PermissionDenied(
            'User is not allowed to access ubicacion(es): {0}.'.format(
                ', '.join(str(value) for value in sorted(missing_ids))
            )
        )
