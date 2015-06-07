import sys
import abc
from abc_base import UbicacionFisica #Importando clase abstracta de Ubicacion Fisica
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from restaurante.models import UbicacionFisica, DetalleUbicacion, RegmaestroUbicacionfisica


class Mesa(UbicacionFisica):

    def __init__(self, nombre, descripcion, sucursal, minimocomensales, maximocomensales):
        #Codigo agrupador de Almacen (no usar textos) - 115
        super(Mesa, self).__init__(self.nombre, self.descripcion, self.sucursal, '115') #Inicializando la clase abstracta
        #Campos adicionales de Ubicacion Fisica que corresponden al Area de Preparacion - Detalle Ubicacion Fisica
        self.minimocomensales = minimocomensales
        self.maximocomensales = maximocomensales

    def save(self): 
        super(Mesa, self).save() #Se salva la informacion de la Ubicacion Fisica de la clase abstracta
        #Guardando la informacion del objeto en BD, existe diferencia si es Nuevo o solo se actualiza
        if self.pk is None:
            detallemesa = DetalleUbicacion (
                 id_ubicacionfisica = super(Mesa, self).id,
                 minimocomensales = self.minimocomensales,
                 maximocomensales = self.maximocomensales,
                 )
        else:
            detallemesa = DetalleUbicacion.objects.get(id_ubicacionfisica=super(Mesa, self).id)
            detallemesa.terminalsalida = self.minimocomensales
            detallemesa.telefono = self.maximocomensales
        end if

        try:
            with transaction.atomic()
               detallemesa.save()
        except IntegrityError e:
            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

    def disable(self):
        # *Validaciones generales para la ubicacion fisica
        super(Mesa, self).disable()
        # *Validacion de que la ubicacion fisica no sea default
        if self.default = True:
            raise ValueError("Ubicacion fisica %uf es default" % (self.id))
        # *Validacion de que la ubicacion fisica no sea asociada con Registro Maestro con saldo diferente de cero
        else:
            mesa = UbicacionFisica.objects.get(id=self.id)
            mesa.estatus = 'C' # Estatus cerrado, ya no podra ser usada en el sistema, solo para consultas
            try:
                with transaction.atomic()
                mesa.save()
            except IntegrityError e:
                #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)
        end if
        
    def get(self, id_ubicacionfisica): 
        super(Mesa, self).get(id_ubicacionfisica)
        mesa_detalle = DetalleUbicacion.objects.get(id_ubicacionfisica=id_ubicacionfisica)
        self.minimocomensales = mesa_detalle.minimocomensales
        self.maximocomensales = mesa_detalle.maximocomensales

