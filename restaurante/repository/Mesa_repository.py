from django.db import IntegrityError
from django.db import transaction

from restaurante.models import UbicacionFisica, DetalleUbicacion, RegmaestroUbicacionfisica, LibroCuentacontable, TipoCuentaContable
from restaurante.repository.Ubicacion_repository import UbicacionFisica_Repo #Importando clase abstracta de Ubicacion Fisica

#from restaurante.data_object.CuentaContable_dataobject import CuentaContable_Repo # clase de repositorio

class Mesa(UbicacionFisica_Repo):

    def __init__(self):
        #Inicializando la clase abstracta
        #Codigo agrupador de Inventario (no usar textos) - 115 - Se considera a la mesa  como almacen
        tipo = int(''.join(map(str,TipoCuentaContable.objects.filter(instancia=self.__class__.__name__).values_list('tipo', flat=True))))
        super(Mesa, self).__init__(tipo)
        #Campos adicionales de Ubicacion Fisica que corresponden al mesa  - Detalle Ubicacion Fisica
        self.id = None
        self.minimocomensales = None
        self.maximocomensales = None

    def save(self): 
        super(Mesa, self).save() #Se salva la informacion de la Ubicacion Fisica de la clase abstracta
        detallemesa = DetalleUbicacion()
        try:
            detallemesa = DetalleUbicacion.objects.get(id_ubicacionfisica=self.id)
        except DetalleUbicacion.DoesNotExist:
            detallemesa.id = None

        if not detallemesa.id:
            detallemesa.id_ubicacionfisica = self.id
            detallemesa.minimocomensales = self.minimocomensales
            detallemesa.maximocomensales = self.maximocomensales
        else:
            detallemesa.minimocomensales = self.minimocomensales
            detallemesa.maximocomensales = self.maximocomensales

        try:
            with transaction.atomic():
               detallemesa.save()
            #self.id = detallemesa.id Quizas no es requerido
        except IntegrityError as e:
            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

    def disable(self):
        # *Validaciones generales para la ubicacion fisica
        super(Mesa, self).disable()
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
            mesa = UbicacionFisica.objects.get(id=self.id)
            mesa.estatus = 'C' # Estatus cerrado, ya no podra ser usada en el sistema, solo para consultas
            try:
                with transaction.atomic():
                    mesa.save()
            except IntegrityError as e:
                #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

    def get(self, id_ubicacionfisica):
        super(Mesa, self).get(id_ubicacionfisica)
        try:
            detallemesa = DetalleUbicacion.objects.get(id_ubicacionfisica=id_ubicacionfisica)
            self.minimocomensales = detallemesa.minimocomensales
            self.maximocomensales = detallemesa.maximocomensales
        except DetalleUbicacion.DoesNotExist:
            #print("El detalle de la ubicacion fisica no existe")
            self.minimocomensales = None
            self.maximocomensales = None

