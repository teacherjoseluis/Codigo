import sys
from Lib.abc import ABCMeta, abstractmethod # Clase para el manejo de clases abstractas
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from restaurante.models import UbicacionFisica, DetalleUbicacion, LibroCuentacontable, DetalleDocumento, AuthUser_UbicacionFisica
from restaurante.data_object.CuentaContable_dataobject import CuentaContable_Repo # clase de repositorio

#from django.db.models import Max
#Clase Abstracta
class UbicacionFisica_Repo(object):
    __metaclass__ = ABCMeta

    def __init__(self, tipo):
        self.id = None
        self.nombre = None
        self.descripcion = None
        self.sucursal = None
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
            ubicacionfisica.id_sucursalsistema = self.sucursal
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
        if DetalleDocumento.objects.get(Q(id_ubicacionfisica1=self.id),~Q(estatus='C') | Q(id_ubicacionfisica2=self.id),~Q(estatus='C')):
            raise ValueError("Ubicacion fisica %uf esta en estatus diferente de cerrado")

        # *Validacion de que la ubicacion fisica no sea asociada con Cuenta Contable con saldo diferente de cero
        if LibroCuentacontable.objects.get(id_cuentacontable=self.cuentacontable,saldo__gt=0):
            raise ValueError("La cuenta contable %uf tiene un saldo mayor a 0" % self.cuentacontable)

    #Asignar la ubicacion fisica como default para la sucursal (lease almacen de recepcion de mercancias)
    @abstractmethod
    def set_default(self): 
        #Poniendo a default=false todas las ubicaciones fisicas
        if self.default is False:
            ubicacionfisica = UbicacionFisica.objects.filter(tipo=self.tipo, estatus=self.estatus, default=True).update(default=False)
            # La ubicacion fisica se marca como default
            ubicacionfisica = UbicacionFisica.objects.get(id=self.id)
            ubicacionfisica.default=True
            try:
                with transaction.atomic():
                    ubicacionfisica.save()
            except IntegrityError as e:
                #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)
    
    #Asignar/Desasignar usuario a/de la ubicacion fisica (add, del)
    @abstractmethod
    def user(self,usuario,accion): 
        # Pendiente de crear una tabla intermedia con el Usuario y su respectivo modelo
        if accion == 'add' :
            # Revisar que el usuario no haya sido ya asociado a la ubicacion fisica, de ya estarlo simplemente no hara nada
            if self.is_user(usuario) is False:
                # De momento esta tabla no existe ni en la BD ni en el modelo
                ubicacion_usuario =  AuthUser_UbicacionFisica (
                    id_ubicacionfisica = self.id,
                    id_usuario = usuario.id
                    )
                try:
                    with transaction.atomic():
                        ubicacion_usuario.save()
                except IntegrityError as e:
                    #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                    print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

        if accion == 'del' :
            # Revisar que el usuario este asociado a la ubicacion fisica
            if self.is_user(usuario) is True:
                # Borrando el registro de la tabla
                AuthUser_UbicacionFisica.objects.filter(id_ubicacionfisica=self.id, id_usuario=usuario.id).delete()

    @abstractmethod
    def is_user(self,usuario):
        #Verificar si determinado usuario esta asociado a la ubicacion fisica
        # Buscar en AuthUser_UbicacionFisica por la relacion con el usuario
        if AuthUser_UbicacionFisica.objects.get(id_ubicacionfisica=self.id, id_usuario=usuario.id):
           return True
        else:
           return False

    #Obtener las existencias de un registro maestro en la ubicacion
    @abstractmethod
    def get_stock(self, registromaestro):
        pass

    #Obtener el balance (Saldo Actual) de la ubicacion fisica
    @abstractmethod
    def get_balance(self): 
        return DetalleUbicacion.objects.get(id_ubicacionfisica=self.id).values_list('saldoactual', flat=True)

#Obtener la ubicacion fisica y su detalle por su Id
    @classmethod
    def get(cls, id_ubicacionfisica):
        #uf = Ubiccion Fisica
        #ud = Ubicacion Fisica Detalle
        uf = UbicacionFisica.objects.get(id=id_ubicacionfisica)
        ud = DetalleUbicacion.objects.get(id_ubicacionfisica=id_ubicacionfisica)
        return cls(uf.nombre, uf.descripcion, uf.sucursal, uf.tipo, ud.direccion, ud.telefono, ud.horarioinicio, ud.horariofin, ud.terminalsalida, ud.minimocomensales, ud.maximocomensales)

