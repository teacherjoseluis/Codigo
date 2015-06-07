import sys
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from restaurante.models import CuentaContable
#from django.db.models import Max

#Clase Abstracta
class CuentaContable(object):

    def __init__(self, nombre, tipo, sucursal):
        self.nombre = nombre
        self.tipo = tipo
        self.cliente = SucursalSistema.objects.get(ID=self.sucursal).values_list('ID_Cliente', flat=True)
        self.estatus = 'A' #Al ser nuevo se le considera activo por default

        # Obteniendo la cuentacontable del padre a partir del tipo de cuenta
        self.cuentacontable_padre = CuentaContable.objects.get(id_cliente=self.id_cliente,id_tipo=self.tipo,id_subcuentacontable='').values_list('ID', flat=True)

    def __str__(self):
        return "%s" % (self.nombre)

    #Guarda o actualiza la ubicacion fisica (diferente del metodo del modelo save)
    def saveas(self):
        if self.pk is None:
            cuentacontable = CuentaContable (
                nombre = self.nombre, 
                tipo = self.tipo, 
                estatus = self.estatus, 
                id_cliente = self.cliente,
                id_subcuentacontable = self.cuentacontable_padre
                )
        else:
            cuentacontable = CuentaContable.objects.get(id=self.id)
            cuentacontable.nombre = self.nombre
            #cuentacontable.tipo = self.tipo
            cuentacontable.estatus = self.estatus
        end if

        try:
            with transaction.atomic()
               cuenta_contable.save() # Salvando la instancia del objeto cuenta contable a fin de que se establezca la relacion entre tablas
        except IntegrityError:
            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
            print ("Existe un error al tratar de guardar el objeto")


    #Deshabilita la cuentacontable
    #def disable(self):
    #    pass
