__author__ = 'teacher'

from django.db import transaction

from restaurante.models import RegistroMaestro, AgrupadorBajonivel, RegmaestroUbicacionfisica, RegmaestroPedimento, RegmaestroCompra, RegmaestroContabilidad, RegmaestroFoto, RegmaestroInventario, RegmaestroVenta
from django.db.models import Sum
from django.db import IntegrityError

class RegMaestro(object):

    def __init__(self):
    # Inicializando la clase de registro maestro
        self.id = None
        self.nombre = None
        self.tipo = None
        self.clasificacion = None
        self.marca = None
        self.estatus = 'A'

    def __unicode__(self):
        return "%s" % (self.nombre)

    def save(self):
        if self.id is None:
            regmaestro = RegistroMaestro ()

        else:
            regmaestro = RegistroMaestro.objects.get(id=self.id)

        regmaestro.nombre = self.nombre
        regmaestro.tipo = self.tipo
        regmaestro.clasificacion = self.clasificacion
        regmaestro.marca = self.marca

        try:
            with transaction.atomic():
               regmaestro.save()
        except IntegrityError as e:
            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

        def disable(self):
        #Revisar si el registro esta asociado a algun platillo o bebida
        #*** Implementar funcionalidad en la clase sucursal a fin de extraer todas las ubicaciones fisicas de la misma y usarlas abajo ***
            if AgrupadorBajonivel.objects.get(id_registromaestro=self.id):
                raise ValueError("Registro Maestro esta actualmente asociado a un platillo %abn " % (AgrupadorBajonivel.id))
            #Revisar si hay existencias en el almacen (get_stock)
            #*** Implementar funcionalidad en la clase sucursal a fin de extraer todas las ubicaciones fisicas de la misma y usarlas abajo ***
            if RegmaestroUbicacionfisica.objects.get(id_registromaestro=self.id).aggregate(Sum('existencias')) > 0:
                raise ValueError("Registro Maestro tiene actualmente existencias mayores a 0" % (AgrupadorBajonivel.id))
            #Revisar si existen documentos con el registro maestro
            registromaestro = RegistroMaestro.objects.get(id=self.id)
            registromaestro.estatus = 'C' # Estatus cerrado, ya no podra ser usada en el sistema, solo para consultas
            try:
                with transaction.atomic():
                    registromaestro.save()
            except IntegrityError as e:
            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

        def get(id_registromaestro):
            registromaestro = RegistroMaestro.objects.get(id=id_registromaestro)
            self.id = registromaestro.id
            self.nombre = registromaestro.nombre
            self.tipo = registromaestro.tipo
            self.clasificacion = registromaestro.clasificacion
            self.marca = registromaestro.marca
            self.estatus = registromaestro.estatus

        @classmethod
        def contexto(type):
        #Punto de declaracion de la clase abstracta RegMaestro_Contexto, se hace aqui a fin de que se haga dentro de la declaracion de la clase Registro Maestro'
            if self.id is None:
                raise IntegrityError("Error dado que el registro maestro no ha sido salvado") #Este error no fue generado por la BD pero lo estoy considerando asi
            else:
                if (type == "UbicacionFisica"): return RegMaestro.Contexto_UbicacionFisica(self.id)
                if (type == "Pedimento"): return RegMaestro.Contexto_Pedimento(self.id)
                if (type == "Foto"): return RegMaestro.Contexto_Foto(self.id)
                if (type == "Contabilidad"): return RegMaestro.Contexto_Contabilidad(self.id)
                if (type == "Compra"): return RegMaestro.Contexto_Compra(self.id)
                if (type == "Venta"): return RegMaestro.Contexto_Venta(self.id)
                if (type == "Inventario"): return RegMaestro.Contexto_Inventario(self.id)
                assert 0, "Error: " + type


            class RegMaestro_Contexto(object):
                def save(self): pass
                def get(self): pass

                ' ***************************** Ubicacion Fisica *********************************'
                class Contexto_UbicacionFisica(RegMaestro.RegMaestro_Contexto):

                    def __init__(self, idregistromaestro):
                        self.id = None
                        self.idregistromaestro = idregistromaestro
                        self.idubicacionfisica = None
                        self.existencias = None

                    def save(self):
                        if self.id is None:
                            contexto = RegmaestroUbicacionfisica ()
                            contexto.id_registromaestro = self.idregistromaestro
                            contexto.id_ubicacionfisica = self.idubicacionfisica
                        else:
                            contexto = RegmaestroUbicacionfisica.objects.get(id_registromaestro=self.id, id_ubicacionfisica=self.idubicacionfisica)

                        contexto.existencias = self.existencias

                        try:
                            with transaction.atomic():
                                contexto.save()
                        except IntegrityError as e:
                        #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

                    def get(self, id_ubicacionfisica):
                        contexto = RegmaestroUbicacionfisica.objects.get(id_registromaestro=self.idregistromaestro, id_ubicacionfisica=id_ubicacionfisica)
                        self.id = contexto.id
                        self.idubicacionfisica = contexto.id_ubicacionfisica
                        self.existencias = contexto.existencias

                ' ***************************** Pedimento *********************************'
                class Contexto_Pedimento(RegMaestro.RegMaestro_Contexto):

                    def __init__(self, idregistromaestro):
                        self.id = None
                        self.idregistromaestro = idregistromaestro
                        self.tamanominimolote = None
                        self.existenciasrequeridas = None
                        self.plancompra = None

                    def save(self):
                        if self.id is None:
                            contexto = RegmaestroPedimento ()
                            contexto.id_registromaestro = self.idregistromaestro

                        else:
                            contexto = RegmaestroPedimento.objects.get(id_registromaestro=self.id)

                        contexto.tamanominimolote = self.tamanominimolote
                        contexto.existenciasrequeridas = self.existenciasrequeridas
                        contexto.plancompra = self.plancompra

                        try:
                            with transaction.atomic():
                                contexto.save()
                        except IntegrityError as e:
                            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

                    def get(self, id_registromaestro):
                        contexto = RegmaestroPedimento.objects.get(id_registromaestro=id_registromaestro)
                        self.id = contexto.id
                        self.tamanominimolote = contexto.tamanominimolote
                        self.existenciasrequeridas = contexto.existenciasrequeridas
                        self.plancompra = contexto.plancompra

                ' ***************************** Foto *********************************'
                class Contexto_Foto(RegMaestro.RegMaestro_Contexto):

                    def __init__(self, idregistromaestro):
                        self.id = None
                        self.idregistromaestro = idregistromaestro
                        self.path_foto = None

                    def save(self):
                        if self.id is None:
                            contexto = RegmaestroFoto ()
                            contexto.id_registromaestro = self.idregistromaestro
                        else:
                            contexto = RegmaestroFoto.objects.get(id_registromaestro=self.id)
                        contexto.path_foto = self.path_foto

                        try:
                            with transaction.atomic():
                                contexto.save()
                        except IntegrityError as e:
                            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

                    def get(self, id_registromaestro):
                        contexto = RegmaestroFoto.objects.get(id_registromaestro=id_registromaestro)
                        self.id = contexto.id
                        self.path_foto = contexto.path_foto

                ' ***************************** Contabilidad *********************************'
                class Contexto_Contabilidad(RegMaestro.RegMaestro_Contexto):

                    def __init__(self, idregistromaestro):
                        self.id = None
                        self.idregistromaestro = idregistromaestro
                        self.idperfilimpuesto = None

                    def save(self):
                        if self.id is None:
                            contexto = RegmaestroContabilidad ()
                            contexto.id_registromaestro = self.idregistromaestro
                        else:
                            contexto = RegmaestroContabilidad.objects.get(id_registromaestro=self.id)
                        contexto.id_perfilimpuesto = self.idperfilimpuesto

                        try:
                            with transaction.atomic():
                                contexto.save()
                        except IntegrityError as e:
                            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

                    def get(self, id_registromaestro):
                        contexto = RegmaestroContabilidad.objects.get(id_registromaestro=id_registromaestro)
                        self.id = contexto.id
                        self.idperfilimpuesto = contexto.id_perfilimpuesto

                ' ***************************** Compra *********************************'
                class Contexto_Compra(RegMaestro.RegMaestro_Contexto):

                    def __init__(self, idregistromaestro):
                        self.id = None
                        self.idregistromaestro = idregistromaestro
                        self.idpresentacioncompra = None
                        self.idpresentacioninventario = None
                        self.equivalenciaentrepresentacion = None
                        self.idunidadmedida = None

                    def save(self):
                        if self.id is None:
                            contexto = RegmaestroCompra ()
                            contexto.id_registromaestro = self.idregistromaestro
                        else:
                            contexto = RegmaestroCompra.objects.get(id_registromaestro=self.id)
                        contexto.id_presentacioncompra=self.idpresentacioncompra
                        contexto.id_presentacioninventario=self.idpresentacioninventario
                        contexto.equivalenciaentrepresentacion=self.equivalenciaentrepresentacion
                        contexto.id_unidadmedida=self.idunidadmedida

                        try:
                            with transaction.atomic():
                                contexto.save()
                        except IntegrityError as e:
                            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

                    def get(self, id_registromaestro):
                        contexto = RegmaestroCompra.objects.get(id_registromaestro=id_registromaestro)
                        self.id = contexto.id
                        self.idpresentacioncompra = contexto.id_presentacioncompra
                        self.idpresentacioninventario = contexto.id_presentacioninventario
                        self.equivalenciaentrepresentacion = contexto.equivalenciaentrepresentacion
                        self.idunidadmedida = contexto.id_unidadmedida

                ' ***************************** Venta *********************************'
                class Contexto_Venta(RegMaestro.RegMaestro_Contexto):

                    def __init__(self, idregistromaestro):
                        self.id = None
                        self.idregistromaestro = idregistromaestro
                        self.idpresentacioninventario = None
                        self.idpresentacionventa = None
                        self.equivalenciaentrepresentaciones = None
                        self.idunidadmedida = None

                    def save(self):
                        if self.id is None:
                            contexto = RegmaestroVenta ()
                            contexto.id_registromaestro = self.idregistromaestro
                        else:
                            contexto = RegmaestroVenta.objects.get(id_registromaestro=self.id)

                        contexto.id_presentacioninventario=self.idpresentacioninventario
                        contexto.id_presentacionconsumo=self.idpresentacionconsumo
                        contexto.equivalenciaentrepresentaciones=self.equivalenciaentrepresentaciones
                        contexto.id_unidadmedida=self.idunidadmedida

                        try:
                            with transaction.atomic():
                                contexto.save()
                        except IntegrityError as e:
                            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

                    def get(self, id_registromaestro):
                        contexto = RegmaestroVenta.objects.get(id_registromaestro=id_registromaestro)
                        self.id = contexto.id
                        self.idpresentacioninventario = contexto.id_presentacioninventario
                        self.idpresentacionconsumo = contexto.id_presentacionconsumo
                        self.equivalenciaentrepresentaciones = contexto.equivalenciaentrepresentaciones
                        self.idunidadmedida = contexto.id_unidadmedida

                ' ***************************** Inventario *********************************'
                class Contexto_Inventario(RegMaestro.RegMaestro_Contexto):

                    def __init__(self, idregistromaestro):
                        self.id = None
                        self.idregistromaestro = idregistromaestro
                        self.idpresentacioninventario = None
                        self.inventarioseguridad = None
                        self.caducidad = None
                        self.localidad = None

                    def save(self):
                        if self.id is None:
                            contexto = RegmaestroInventario ()
                            contexto.id_registromaestro = self.idregistromaestro
                        else:
                            contexto = RegmaestroInventario.objects.get(id_registromaestro=self.id)

                        contexto.idpresentacioninventario=self.idpresentacioninventario
                        contexto.inventarioseguridad=self.inventarioseguridad
                        contexto.caducidad=self.caducidad
                        contexto.localidad=self.localidad

                        try:
                            with transaction.atomic():
                                contexto.save()
                        except IntegrityError as e:
                            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
                            print ("Existe un error al tratar de guardar el objeto %err", e.pgcode)

                    def get(self, id_registromaestro):
                        contexto = RegmaestroCompra.objects.get(id_registromaestro=id_registromaestro)
                        self.id = contexto.id
                        self.idpresentacioninventario = contexto.idpresentacioninventario
                        self.inventarioseguridad = contexto.inventarioseguridad
                        self.caducidad = contexto.caducidad
                        self.localidad = contexto.localidad


        '--------------------------------------------------------------------------------------------------------------------------'
'''
a = RegMaestro(id, nombre, tipo, clasificacion, marca) -- Crea un registro maestro
b = a.contexto("UbicacionFisica")
b.(id, idubicacionfisica, existencias) -- Dentro de la instancia de registro maestro, crea un contexto de ubicacion fisica

'''
