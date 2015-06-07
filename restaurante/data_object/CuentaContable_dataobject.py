import sys
from django.db import IntegrityError
from django.db import transaction
from django.db import DatabaseError
from django.db.models import Q
from restaurante.models import CuentaContable, SucursalSistema
#from django.db.models import Max

#Clase Abstracta
class CuentaContable_Repo(object):

    def __init__(self, nombre, tipo, sucursal):
        self.id = None
        self.nombre = nombre
        self.tipo = tipo
        self.sucursal = sucursal
        self.cliente = SucursalSistema.objects.get(id=sucursal).id_cliente
        self.estatus = 'A' #Al ser nuevo se le considera activo por default

        # Obteniendo la cuentacontable del padre a partir del tipo de cuenta
        try:
            self.cuentacontable_padre = CuentaContable.objects.get(id_cliente=self.cliente,sub_tipo=self.tipo,id_subcuentacontable=None).id
        except DatabaseError as e:
            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

    def __str__(self):
        return "%s" % (self.nombre)

    #Guarda o actualiza la ubicacion fisica (diferente del metodo del modelo save)
    def save(self):
        if self.id is None:
            cuentacontable = CuentaContable()
            cuentacontable.nombre = self.nombre
            cuentacontable.tipo = self.tipo
            cuentacontable.estatus = self.estatus
            cuentacontable.id_cliente = self.cliente
            cuentacontable.id_subcuentacontable = self.cuentacontable_padre

        else:
            cuentacontable = CuentaContable.objects.get(id=self.id)
            cuentacontable.nombre = self.nombre
            #cuentacontable.tipo = self.tipo
            cuentacontable.estatus = self.estatus

        try:
            with transaction.atomic():
               cuentacontable.save() # Salvando la instancia del objeto cuenta contable a fin de que se establezca la relacion entre tablas
            self.id = cuentacontable.id
        except IntegrityError:
            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
            print ("Existe un error al tratar de guardar el objeto")

    #Deshabilita la cuentacontable
    #def disable(self):
    #    pass
