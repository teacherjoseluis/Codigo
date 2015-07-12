from django.db import IntegrityError
from django.db import transaction

from restaurante.models import UbicacionFisica, DetalleUbicacion, RegmaestroUbicacionfisica, LibroCuentacontable, TipoCuentaContable
from restaurante.repository.Ubicacion_repository import UbicacionFisica_Repo #Importando clase abstracta de Ubicacion Fisica

class Caja(UbicacionFisica_Repo):

    def __init__(self):
        #Inicializando la clase abstracta
        #Codigo agrupador de Caja (no usar textos)
        tipo = int(''.join(map(str,TipoCuentaContable.objects.filter(instancia=self.__class__.__name__).values_list('tipo', flat=True))))
        super(Caja, self).__init__(tipo)
        #Campos adicionales de Ubicacion Fisica que corresponden a la Caja
        self.id = None
        self.terminalsalida = None
        self.telefono = None
        self.horariorecepcion = None
        self.saldoactual = None
        self.impresora = None

    def save(self): 
        super(Caja, self).save() #Se salva la informacion de la Ubicacion Fisica de la clase abstracta
        detallecaja = DetalleUbicacion()
        try:
            detallecaja = DetalleUbicacion.objects.get(id_ubicacionfisica=self.id)
        except DetalleUbicacion.DoesNotExist:
            detallecaja.id = None

        if not detallecaja.id:
            detallecaja.id_ubicacionfisica = self.id
            detallecaja.terminalsalida = self.terminalsalida
            detallecaja.telefono = self.telefono
            detallecaja.horariorecepcion = self.horariorecepcion
            detallecaja.saldoactual = self.saldoactual
            detallecaja.impresora = self.impresora

        else:
            detallecaja.terminalsalida = self.terminalsalida
            detallecaja.telefono = self.telefono
            detallecaja.horariorecepcion = self.horariorecepcion
            detallecaja.saldoactual = self.saldoactual
            detallecaja.impresora = self.impresora

        try:
            with transaction.atomic():
               detallecaja.save()
            self.id = detallecaja.id
        except IntegrityError as e:
            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

    def disable(self):
        # *Validaciones generales para la ubicacion fisica
        super(Caja, self).disable()
        # *Validacion de que la ubicacion fisica no sea default
        if self.default is True:
            raise ValueError("Ubicacion fisica %uf es default" % self.id)
        # *Validacion de que la ubicacion fisica no sea asociada con Registro Maestro con saldo diferente de cero
        #Registros con existencia mayor a cero

        #if LibroCuentacontable.objects.filter(id_cuentacontable=self.cuentacontable, saldo__gt=0).count():
        #    raise ValueError("La cuenta contable %uf tiene un saldo mayor a 0" % self.cuentacontable)'
        #TODO: revisar que situaciones hay que validar para poder desactivar la caja
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
        super(Caja, self).get(id_ubicacionfisica)
        try:
            detallecaja = DetalleUbicacion.objects.get(id_ubicacionfisica=id_ubicacionfisica)
            self.terminalsalida = detallecaja.terminalsalida
            self.telefono = detallecaja.telefono
            self.horariorecepcion = detallecaja.horariorecepcion
            self.saldoactual = detallecaja.saldoactual
            self.impresora = detallecaja.impresora
        except DetalleUbicacion.DoesNotExist:
            #print("El detalle de la ubicacion fisica no existe")
            self.terminalsalida = None
            self.telefono = None
            self.horariorecepcion = None
            self.saldoactual = None
            self.impresora = None