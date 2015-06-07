#import sys
import abc
from abc_base import UbicacionFisica #Importando clase abstracta de Ubicacion Fisica
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from restaurante.models import UbicacionFisica, DetalleUbicacion, RegmaestroUbicacionfisica


class Almacen(UbicacionFisica):

    def disable(self):
        # *Validaciones generales para la ubicacion fisica
        super(Almacen, self).disable()
        # *Validacion de que la ubicacion fisica no sea default
        if self.default = True:
            raise ValueError("Ubicacion fisica %uf es default" % (self.id))
        # *Validacion de que la ubicacion fisica no sea asociada con Registro Maestro con saldo diferente de cero
        else if RegmaestroUbicacionfisica.objects.get(id_ubicacionfisica=self.id, existencias>0): #Registros con existencia mayor a cero
            raise ValueError("Ubicacion fisica %uf aun tiene existencias" % (self.id))
        else:
            almacen = UbicacionFisica.objects.get(id=self.id)
            almacen.estatus = 'C' # Estatus cerrado, ya no podra ser usada en el sistema, solo para consultas
            try:
                with transaction.atomic()
                almacen.save()
            except IntegrityError e:
                #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)
        end if  

    def get_stock(self, registromaestro): 
        # Este metodo recibe como parametro un registro maestro para devolver el monto en existencias de este en el almacen
        return RegmaestroUbicacionfisica.objects.get(id_ubicacionfisica=self.id, id_registromaestro=registromaestro.id).values_list('existencias', flat=True)
        
    #def get_balance(self): 
        #pass
