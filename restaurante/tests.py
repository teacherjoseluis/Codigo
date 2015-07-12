# http://cgoldberg.github.io/python-unittest-tutorial/
import datetime


from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from restaurante.models import *
from restaurante.repository.AreaPreparacion_repository import AreaPreparacion
from restaurante.repository.Ubicacion_repository import UbicacionFisica_Repo

from restaurante.factory.RegMaestro_factory import RegMaestro

    # Ubicacion fisica
class UFRepo_Validacion(TestCase):
    #save
    """Existe la ubicacion fisica en Detalle Documento, Estatus = 1"""

    def test_uf_sucursalvalida(self):
        # A fin de mantener la consistencia en BD, se debera asegurar que la sucursal exista
        a = AreaPreparacion()
        a.sucursal = 666
        self.assertRaises(ObjectDoesNotExist, a.save)

    def test_uf_sucursalnoexiste(self):
        # A fin de mantener la consistencia en BD, se debera asegurar que la sucursal exista
        a = AreaPreparacion()
        a.sucursal = None
        self.assertRaises(ValueError, a.save)

    #disable
    """Existe la ubicacion fisica en Detalle Documento, Estatus = 1"""
    #Como precondicion se necesita trabajar con una ubicacion fisica que exista en un Detalle Documento con estatus Activo
    #Hasta este momento 06/23 no se ha desarrollado la funcionalidad para crear el detalle del documento
    def test_uf_documento(self):
        pass

    """Existe Libro Cuenta Contable, Saldo > 0"""
    # Me gustaria probar esta funcionalidad con un ingreso de mercancia en el almacen o area de preparacion a fin de incrementar el saldo desde el caso de prueba
    def test_uf_cuentacontable(self):
        pass

    #user
    """Usuario invalido"""
    def test_uf_usuarioinvalido(self):
        area = AreaPreparacion()
        self.assertRaises(ObjectDoesNotExist, area.user, 999, 'add') #Recordar que la validacion se hace sobre los usuarios de la sucursal

    """Usuario no asociado a la sucursal de la UF"""
    def test_uf_usuarionoasociado(self):
         area = AreaPreparacion()
         area.get(1) #Ubicacion fisica cuya sucursal sea diferente a la del usuario 2
         self.assertRaises(ObjectDoesNotExist, area.user, 2,'add') # Asociando un usuario existente pero no de la misma sucursal que la UF

    """Usuario Comando invalido"""
    def test_uf_comandoinvalido(self):
        area = AreaPreparacion()
        self.assertRaises(ValueError, area.user, 1,'xxx')
         
    #is_user
    #Usuario invalido
    #Ya no se hara validacion aqui, ya que se esta consideranto en uf_usuarioinvalido()

    #get
    """Ubicacion fisica no existente"""
    def test_uf_ufinvalida(self):
         area = AreaPreparacion()
         self.assertRaises(ObjectDoesNotExist, area.get, 999) #Corresponde a una ubicacion fisica invalida

    """Tipo no corresponde a la clase"""
    def test_uf_tipoinvalido(self):
         area = AreaPreparacion()
         self.assertRaises(ValueError, area.get, 3) #Suponiendo que la UF 2 no corresponde al mismo tipo del AreaPreparacion

    #get_stock
    """Registro maestro no existente"""
    def test_uf_regmaestroinvalido(self):
         area = AreaPreparacion()
         self.assertRaises(ObjectDoesNotExist, area.get_stock, 999) #Registro maestro invalido

    """Registro maestro existente pero no asociado a la UF"""
    def test_uf_regmaestronoasociado(self):
         area = AreaPreparacion()
         area.get(1) #Area que no tiene el Registro Maestro 2 asociada
         self.assertRaises(ObjectDoesNotExist, area.get_stock, 2) # Solicitando stock de un registro maestro existente pero actualmente no asocidado a la UF

    #get_balance
    #No considero que se ameriten pruebas unitarias para este metodo

    # Metodos nuevos relacionados con estatus, no es necesario instanciar para obtener los valores. Seran de uso primordialmente fuera del ambito de la UF.
    #get_status
    """Simplemente obtendra el estatus de la instancia. Esto servira para propositos de validacion"""
    def test_uf_getstatus(self):
         #La definire de una vez porque me interesa manejarla ya. Va a fallar actualmente por no existir el metodo
         self.assertIsNotNone(UbicacionFisica_Repo.get_status, 1) #Los estatus se procesaran de forma numerica: 1)Activo, 2)Bloqueado, 3)Inactivo

    def test_uf_getstatusinvalido(self):
         #La definire de una vez porque me interesa manejarla ya. Va a fallar actualmente por no existir el metodo
         self.assertRaises(ObjectDoesNotExist,UbicacionFisica_Repo.get_status, 999) #Los estatus se procesaran de forma numerica: 1)Activo, 2)Bloqueado, 3)Inactivo


    #""" Estatus con tipo invalido"""
    #def test_uf_getstatustipoinvalido(self):
    #     self.assertRaises(UbicacionFisica.ValidationError, AreaPreparacion.get_status(2)) #Suponiendo que la UF 2 no corresponde al mismo tipo del AreaPreparacion

    #set_status
    #Implementaria logica mas estricta de lo que se deberia cumplir a fin de que se diera un cambio de estatus para la clase UF
    """ Set status """
    def test_uf_setstatusinvalido(self):
         #Ejecucion exitosa a estatus Bloqueado para el area 1
         self.assertRaises(ObjectDoesNotExist,UbicacionFisica_Repo.set_status, 999, 2) #Los estatus se procesaran de forma numerica: 1)Activo, 2)Bloqueado, 3)Inactivo

         #TODO: Es necesario que esta funcionalidad sea probada con diferentes perfiles de usuario porque no todos lo podran realizar. El metodo set_status debera verificar el usuario actualmente registrado en el sistema, aunque de momento esta validacion puede ser pasada por alto.

    #""" Set status con tipo invalido """
    #def test_uf_setstatustipoinvalido(self):
    #     self.assertRaises(UbicacionFisica.ValidationError, AreaPreparacion.set_status(2, 2)) #Suponiendo que la UF 2 no corresponde al mismo tipo del AreaPreparacion


#Registro Maestro
class RegMas_Validacion(TestCase):

    #get_registromaestro no existe
    def test_regmas_invalido(self):
        a = RegMaestro()
        self.assertRaises(ObjectDoesNotExist, a.get, 999)

    #la ubicacion fisica asignada al registro maestro no existe (save, get)
    def test_regmas_uf_invalida_save(self):
        a = RegMaestro()
        b = a.contexto(a, "UbicacionFisica")
        b.idubicacionfisica = 999
        self.assertRaises(ObjectDoesNotExist, b.save)

    #la ubicacion fisica asignada al registro maestro no existe (save, get)
    def test_regmas_uf_invalida_get(self):
        a = RegMaestro()
        b = a.contexto(a, "UbicacionFisica")
        self.assertRaises(ObjectDoesNotExist, b.get, 999)

    #se intenta actualizar la ubicacion fisica de un registro existente
    def test_regmas_uf_change_uf(self):
        a = RegMaestro()
        a.get(1)
        b = a.contexto(a, "UbicacionFisica")
        b.get(3)
        b.idubicacionfisica = 2
        self.assertRaises(ValueError, b.save)

    #se intenta actualizar el registro maestro de un registro existente
    def test_regmas_uf_change_rm(self):
        a = RegMaestro()
        a.get(1)
        b = a.contexto(a, "UbicacionFisica")
        b.get(3)
        b.idregistromaestro = 2
        self.assertRaises(ValueError, b.save)

    #multiples ubicaciones fisicas no se pueden salvar
    #Previamente ya existe una ubicacion fisica 1
    def test_regmas_uf_many_uf(self):
        a = RegMaestro()
        a.get(1)
        b = a.contexto(a, "UbicacionFisica")
        b.idubicacionfisica = 3
        self.assertRaises(ValueError, b.save)

    #se intenta actualizar el registro maestro de un registro existente
    def test_regmas_ped_change_rm(self):
        a = RegMaestro()
        a.get(1)
        b = a.contexto(a, "Pedimento")
        b.get(1)
        b.idregistromaestro = 2
        self.assertRaises(ValueError, b.save)

    #multiples registros maestros
    def test_regmas_ped_many_rm(self):
        a = RegMaestro()
        b = a.contexto(a, "Pedimento")
        b.idregistromaestro = 1
        self.assertRaises(ValueError, b.save)