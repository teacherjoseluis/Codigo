import sys
from Lib.abc import ABCMeta, abstractmethod # Clase para el manejo de clases abstractas
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from restaurante.models import UbicacionFisica, DetalleUbicacion, LibroCuentacontable, DetalleDocumento, AuthUser_UbicacionFisica, SucursalSistema
from restaurante.data_object.CuentaContable_dataobject import CuentaContable_Repo # clase de repositorio
from django.core.exceptions import ObjectDoesNotExist

#from django.db.models import Max
#Clase Abstracta
class UbicacionFisica_Repo(object):
    __metaclass__ = ABCMeta

    def __init__(self, tipo):
        self.id = None
        self.nombre = None
        self.descripcion = None
        self.sucursal = None
        #self.tipo = int(''.join(map(str, tipo)))
        self.tipo = tipo
        self.default = False
        self.cuentacontable = None
        self.estatus = 'A' #Al ser nuevo se le considera activo por default

    @abstractmethod
    def __unicode__(self):
        # Sustituye a __str__
        return "%s" % self.nombre

    #Guarda o actualiza la ubicacion fisica (diferente del metodo del modelo save)
    @abstractmethod
    def save(self):
        if self.id is None:
            ubicacionfisica = UbicacionFisica()
            if self.sucursal is not None:
                #int(''.join(map(str,SucursalSistema.objects.filter(id=self.sucursal).values_list('id', flat=True))))
                if not SucursalSistema.objects.filter(id=self.sucursal):
                    raise(ObjectDoesNotExist)
                #print ("La sucursal proporcionada no fue encontrada")
            else:
                raise(ValueError)
                #ubicacionfisica.id_sucursalsistema = self.sucursal

            try:
                 cuenta_ubicacionfisica = CuentaContable_Repo(self.nombre, self.tipo, self.sucursal)
                 cuenta_ubicacionfisica.save()
                 ubicacionfisica.cuenta_contable = cuenta_ubicacionfisica.id
            except InterruptedError as e:
                print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

        else:
            ubicacionfisica = UbicacionFisica.objects.get(id=self.id)

        ubicacionfisica.nombre = self.nombre
        ubicacionfisica.descripcion = self.descripcion
        ubicacionfisica.estatus = self.estatus

        try:
            with transaction.atomic():
               ubicacionfisica.save()
            self.id = ubicacionfisica.id
        except IntegrityError as e:
            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

    #Deshabilita la ubicacion fisica
    @abstractmethod
    def disable(self):
        # *Validacion de que la ubicacion fisica no sea asociada con Documento no cerrado
        if DetalleDocumento.objects.filter(id_ubicacionfisica1=self.id).exclude(estatus='C').count():
            raise ValueError("Ubicacion fisica %uf esta en estatus diferente de cerrado")

        if DetalleDocumento.objects.filter(id_ubicacionfisica2=self.id).exclude(estatus='C').count():
            raise ValueError("Ubicacion fisica %uf esta en estatus diferente de cerrado")

        # *Validacion de que la ubicacion fisica no sea asociada con Cuenta Contable con saldo diferente de cero
        if LibroCuentacontable.objects.filter(id_cuentacontable=self.cuentacontable,saldo__gt=0).count():
            raise ValueError("La cuenta contable %uf tiene un saldo mayor a 0" % self.cuentacontable)

    #Asignar la ubicacion fisica como default para la sucursal (lease almacen de recepcion de mercancias)
    '''@abstractmethod
    def set_default(self): 
        #Poniendo a default=false todas las ubicaciones fisicas
        if self.default is False:
            try:
                ubicacionfisica = UbicacionFisica.objects.filter(tipo=self.tipo, default=True).update(default=False)
            except:
                print ("Ubicacion fisica no encontrada")
            # La ubicacion fisica se marca como default
            ubicacionfisica = UbicacionFisica.objects.get(id=self.id)
            ubicacionfisica.default=True
            try:
                with transaction.atomic():
                    ubicacionfisica.save()
            except IntegrityError as e:
                #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)
    '''
    #Asignar/Desasignar usuario a/de la ubicacion fisica (add, del)
    @abstractmethod
    def user(self,usuario,accion): 
        # Pendiente de crear una tabla intermedia con el Usuario y su respectivo modelo
        if accion == 'add' :
            # Revisar que el usuario no haya sido ya asociado a la ubicacion fisica, de ya estarlo simplemente no hara nada
            if self.is_user(usuario) is False:
                # De momento esta tabla no existe ni en la BD ni en el modelo
                ubicacion_usuario =  AuthUser_UbicacionFisica (
                    ubicacionfisica = self.id,
                    user = usuario
                    )
                try:
                    with transaction.atomic():
                        ubicacion_usuario.save()
                except IntegrityError as e:
                    #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                    print ("Existe un error al tratar de guardar el objeto")

        if accion == 'del' :
            # Revisar que el usuario este asociado a la ubicacion fisica
            if self.is_user(usuario) is True:
                # Borrando el registro de la tabla
                AuthUser_UbicacionFisica.objects.filter(ubicacionfisica=self.id, user=usuario).delete()

    @abstractmethod
    def is_user(self,usuario):
        #Verificar si determinado usuario esta asociado a la ubicacion fisica
        # Buscar en AuthUser_UbicacionFisica por la relacion con el usuario
        try:
            if AuthUser_UbicacionFisica.objects.filter(ubicacionfisica=self.id, user=usuario):
                return True
            else:
                return False
        except AuthUser_UbicacionFisica.DoesNotExist:
            return False

    #Obtener las existencias de un registro maestro en la ubicacion
    @abstractmethod
    def get_stock(self, registromaestro):
        pass

    #Obtener el balance (Saldo Actual) de la ubicacion fisica
    @abstractmethod
    def get_balance(self): 
        return DetalleUbicacion.objects.filter(id_ubicacionfisica=self.id).values_list('saldoactual', flat=True)

#Obtener la ubicacion fisica y su detalle por su Id
    @abstractmethod
    def get(self, id_ubicacionfisica):
        try:
            ubicacionfisica = UbicacionFisica.objects.get(id=id_ubicacionfisica)
            self.id = ubicacionfisica.id
            self.nombre = ubicacionfisica.nombre
            self.descripcion = ubicacionfisica.descripcion
            self.sucursal = ubicacionfisica.id_sucursalsistema
            self.tipo = ubicacionfisica.tipo
            self.default = ubicacionfisica.default
            self.cuentacontable = ubicacionfisica.cuenta_contable
            self.estatus = ubicacionfisica.estatus
        except DetalleUbicacion.DoesNotExist:
            self.id = None
            self.nombre = None
            self.descripcion = None
            self.sucursal = None
            self.tipo = None
            self.default = None
            self.cuentacontable = None
            self.estatus = None
