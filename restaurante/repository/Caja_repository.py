import sys
import abc
from abc_base import UbicacionFisica #Importando clase abstracta de Ubicacion Fisica
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from restaurante.models import UbicacionFisica, DetalleUbicacion, RegmaestroUbicacionfisica


class Caja(UbicacionFisica):

    def __init__(self, nombre, descripcion, sucursal, terminalsalida, telefono):
        #Codigo agrupador de Caja (no usar textos) - 101
        super(UbicacionFisica, self).__init__(self.nombre, self.descripcion, self.sucursal, '101') #Inicializando la clase abstracta
        #Campos adicionales de Ubicacion Fisica que corresponden al Area de Preparacion - Detalle Ubicacion Fisica
        self.terminalsalida = terminalsalida
        self.telefono = telefono

    def save(self): 
        super(UbicacionFisica, self).save() #Se salva la informacion de la Ubicacion Fisica de la clase abstracta
        #Guardando la informacion del objeto en BD, existe diferencia si es Nuevo o solo se actualiza
        if self.pk is None:
            detallecaja = DetalleUbicacion (
                 id_ubicacionfisica = super(Caja, self).id,
                 terminalsalida = self.terminalsalida,
                 telefono = self.telefono,
                 )
        else:
            detallecaja = DetalleUbicacion.objects.get(id_ubicacionfisica=super(Caja, self).id)
            detallecaja.terminalsalida = self.terminalsalida
            detallecaja.telefono = self.telefono
        end if

        try:
            with transaction.atomic()
               detallecaja.save()
        except IntegrityError e:
            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

    def disable(self):
        # *Validaciones generales para la ubicacion fisica
        super(Caja, self).disable()
        # *Validacion de que la ubicacion fisica no sea default
        if self.default = False:
            raise ValueError("Ubicacion fisica %uf es default" % (self.id))
        # *Validacion de que la ubicacion fisica no sea asociada con Registro Maestro con saldo diferente de cero
        else:
            caja = UbicacionFisica.objects.get(id=self.id)
            caja.estatus = 'C' # Estatus cerrado, ya no podra ser usada en el sistema, solo para consultas
            try:
                with transaction.atomic()
                caja.save()
            except IntegrityError e:
                #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)
        end if
        
    def get(self, id_ubicacionfisica): 
        super(Caja, self).get(id_ubicacionfisica)
        caja_detalle = DetalleUbicacion.objects.get(id_ubicacionfisica=id_ubicacionfisica)
        self.terminalsalida = caja_detalle.terminalsalida
        self.telefono = caja_detalle.telefono

