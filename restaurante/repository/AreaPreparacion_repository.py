from django.db import IntegrityError
from django.db import transaction

from restaurante.models import UbicacionFisica, DetalleUbicacion, RegmaestroUbicacionfisica, TipoCuentaContable
from restaurante.repository.Ubicacion_repository import UbicacionFisica_Repo #Importando clase abstracta de Ubicacion Fisica

#from restaurante.data_object.CuentaContable_dataobject import CuentaContable_Repo # clase de repositorio

class AreaPreparacion(UbicacionFisica_Repo):

    def __init__(self):
        #Inicializando la clase abstracta
        #Codigo agrupador de Inventario (no usar textos) - 115 - Se considera a la area de preparacion como almacen
        #tipo = 115
        #tipo = TipoCuentaContable.objects.filter(instancia=self.__class__.__name__).values_list('tipo', flat=True)
        tipo = int(''.join(map(str,TipoCuentaContable.objects.filter(instancia=self.__class__.__name__).values_list('tipo', flat=True))))
        super(AreaPreparacion, self).__init__(tipo)
        #Campos adicionales de Ubicacion Fisica que corresponden al Area de Preparacion - Detalle Ubicacion Fisica
        self.id = None
        self.terminalsalida = None
        self.telefono = None
        self.horariorecepcion = None

    def save(self): 
        super(AreaPreparacion, self).save() #Se salva la informacion de la Ubicacion Fisica de la clase abstracta
        detallearea = DetalleUbicacion()
        try:
            detallearea = DetalleUbicacion.objects.get(id_ubicacionfisica=self.id)
        except DetalleUbicacion.DoesNotExist:
            detallearea.id = None

        if not detallearea.id:
            detallearea.id_ubicacionfisica = self.id
            detallearea.terminalsalida = self.terminalsalida
            detallearea.telefono = self.telefono
            detallearea.horariorecepcion = self.horariorecepcion
        else:
            detallearea.terminalsalida = self.terminalsalida
            detallearea.telefono = self.telefono
            detallearea.horariorecepcion = self.horariorecepcion

        try:
            with transaction.atomic():
               detallearea.save()
            #self.id = detallearea.id Quizas no es requerido
        except IntegrityError as e:
            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

    def disable(self):
        # *Validaciones generales para la ubicacion fisica
        super(AreaPreparacion, self).disable()
        # *Validacion de que la ubicacion fisica no sea default
        if self.default is True:
            raise ValueError("Ubicacion fisica %uf es default" % self.id)
        # *Validacion de que la ubicacion fisica no sea asociada con Registro Maestro con saldo diferente de cero
        #Registros con existencia mayor a cero

        #if LibroCuentacontable.objects.filter(id_cuentacontable=self.cuentacontable, saldo__gt=0).count():
        #    raise ValueError("La cuenta contable %uf tiene un saldo mayor a 0" % self.cuentacontable)'

        if RegmaestroUbicacionfisica.objects.filter(id_ubicacionfisica=self.id, existencias__gt=0):
            raise ValueError("Ubicacion fisica %uf aun tiene existencias" % self.id)
        else:
            area = UbicacionFisica.objects.get(id=self.id)
            area.estatus = 'C' # Estatus cerrado, ya no podra ser usada en el sistema, solo para consultas
            try:
                with transaction.atomic():
                    area.save()
            except IntegrityError as e:
                #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

    def get(self, id_ubicacionfisica):
        super(AreaPreparacion, self).get(id_ubicacionfisica)
        try:
            detallearea = DetalleUbicacion.objects.get(id_ubicacionfisica=id_ubicacionfisica)
            self.terminalsalida = detallearea.terminalsalida
            self.telefono = detallearea.telefono
            self.horariorecepcion = detallearea.horariorecepcion
        except DetalleUbicacion.DoesNotExist:
            #print("El detalle de la ubicacion fisica no existe")
            self.terminalsalida = None
            self.telefono = None
            self.horariorecepcion = None

    def get_stock(self, registromaestro): 
        # Este metodo recibe como parametro un registro maestro para devolver el monto en existencias de este en el almacen
        try:
         existencias = RegmaestroUbicacionfisica.objects.filter(id_ubicacionfisica=self.id, id_registromaestro=registromaestro).values_list('existencias', flat=True)
        except RegmaestroUbicacionfisica.DoesNotExist:
         existencias = None
        return existencias
