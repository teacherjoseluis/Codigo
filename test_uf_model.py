__author__ = 'teacher'

# http://cgoldberg.github.io/python-unittest-tutorial/

import datetime
from django.test import TestCase
from django.db import IntegrityError
from restaurante.repository import Almacen_repository, AreaPreparacion_repository, Caja_repository, Mesa_repository

"""
Proposito de la prueba: Mantener la consistencia de datos, evitar la insercion y modificacion de registros con datos invalidos, mantener la integridad referencial.

Class Almacen, Area Preparacion, Caja, Mesa - Pruebas
	__init__
		1. nombre o descripcion viene vacio
		2. la sucursal existe y corresponde a una sucursal activa
	save
		insert
			1. Campos vacios vienen correctamente formateados
			2. El ID del padre existe antes de insertar el detalle
		update
			1. No permitir la modificacion del tipo, sucursal, cuenta contable, estatus a cerrado
			2. Campos vacios vienen correctamente formateados
	disable

	get
		1. ubicacion fisica no existente
		2. valor no numerico
	get_stock
		1. Registro maestro inexistente
		2. Registro maestro no encontrado en la ubicacion fisica

Ubicacion Fisica
	user
		1. El usuario no existe
		2. El usuario ya esta asociado a la ubicacion
		3. La accion es un nombre invalido (no 'add' or 'del')
	is_user
		1. El usuario no existe
	get_balance
		1. No existe un valor para el saldo actual de la ubicacion fisica
"""

class UFRepo_Validacion(TestCase):
     #datos de prueba
     ubicacionfisica_id = 1
     nombre = "UbicacionFisica1"
     descripcion = "Esta es la descripcion de la ubicacion fisica 1"
     sucursal = "1"
     direccion = "Alguna direccion para la ubicacion fisica #1"
     telefono = "999-888-777"
     horarioinicio = datetime.time(0, 0, 0, 0)
     horariofin = datetime.time(12, 0, 0, 0)

    ''' Esto lo pienso controlar en una capa superior (Vista)

    def valores_invalidos(self):
        # Campos del objeto no deben incluir simbolos
        nombre = "%$@!_+  hfdjfh"
        descripcion = "%$@!_+  hfdjfh"
        horarioinicio = "%$@!_+  hfdjfh" #deben ser de formato hora
        horariofin = "%$@!_+  hfdjfh" #deben ser de formato hora
        almacen = Almacen(nombre, descripcion, sucursal, direccion, telefono, horarioinicio, horariofin)
        self.assertRaises(ValueError)
        # Terminal salida no ha de contener simbolos y/o espacios
        terminalsalida = "%$@!_+  hfdjfh" #aun no determino que debe ser
        areadepreparacion = AreaPreparacion(nombre, descripcion, sucursal, terminalsalida, telefono)
        self.assertRaises(ValueError)
        caja = Caja(nombre, descripcion, sucursal, terminalsalida, telefono)
        self.assertRaises(ValueError)
        # max y min deben ser valores numericos entre 1 y 10
        minimocomensales = "%$@!_+  hfdjfh"
        maximocomensales = "%$@!_+  hfdjfh"
        mesa = Mesa(nombre, descripcion, sucursal, minimocomensales, maximocomensales)
        self.assertRaises(ValueError)

    '''

    '''  Esta es una validacion de capa de negocio
    def numerocomensales_invalido(self):
        # Minimo de comensales no sera mayor que el maximo
        minimocomensales = 4
        maximocomensales = 1
        mesa = Mesa(nombre, descripcion, sucursal, minimocomensales, maximocomensales)
        self.assertRaises(ValueError)
    '''

    ''' Validacion de capa de vista
    def campos_vacios_init(self):
        # Campos escenciales como nombre, descripcion y sucursal no deberan estar vacios
        nombre = ""
        descripcion = ""
        sucursal = None
        almacen = Almacen(nombre, descripcion, sucursal, direccion, telefono, horarioinicio, horariofin)
        self.assertRaises(ValueError)
        areadepreparacion = AreaPreparacion(nombre, descripcion, sucursal, terminalsalida, telefono)
        self.assertRaises(ValueError)
        caja = Caja(nombre, descripcion, sucursal, terminalsalida, telefono)
        self.assertRaises(ValueError)
        mesa = Mesa(nombre, descripcion, sucursal, minimocomensales, maximocomensales)
        self.assertRaises(ValueError)
    '''

    #Esta prueba no esta mal sin embargo hay que considerar que la sucursal no sera de libre asignacion y se trabajara sobre ya existentes '''
    def sucursal_valida(self):
        # A fin de mantener la consistencia en BD, se debera asegurar que la sucursal exista
        sucursal = 999
        almacen = Almacen(nombre, descripcion, sucursal, direccion, telefono, horarioinicio, horariofin)
        self.assertRaises(IntegrityError)

    ''' Validacion de la capa de Vista
    def campos_vacios_formato(self):
        # Para mantener la limpieza en BD, se deberan remover los espacios vacios (no asi entre palabras)
        direccion = "  direccion1  "
        telefono = "    "
        almacen = Almacen(nombre, descripcion, sucursal, direccion, telefono, horarioinicio, horariofin)
        self.assertEqual(almacen.direccion, "direccion1")
        self.assertEqual(almacen.telefono, "")
    '''

    ''' Creo que esta prueba es redundante
    def ubicacionfisica_existe(self):
        # Para asegurarse que se genere la ubicacion fisica al guardar
        almacen = Almacen(nombre, descripcion, sucursal, direccion, telefono, horarioinicio, horariofin)
        almacen.save()
        self.assertIsNotNone(almacen.pk)
    '''

    # Esta pudiera ser redundante pero la considerare ya que se trata de una entidad externa '''
    def cuentacontable_existe(self):
        # Para asegurarse que se genere la cuenta contable de la ubicacion fisica en su creacion
        almacen = Almacen(nombre, descripcion, sucursal, direccion, telefono, horarioinicio, horariofin)
        almacen.save()
        self.assertIsNotNone(almacen.cuentacontable)

    ''' Me gustaria que se pudiera controlar en este nivel, los campos de solo lectura pero agrega mucha complejidad a la clase, se tendria que implementar algo en la capa de negocio
    def update_camposnomodificables(self):
        # Existen ciertos campos que de modificarse, se alteraria la integridad de las relaciones en BD por lo tanto no deberia permitirse
        almacen = Almacen(ubicacionfisica_id)
        #almacen.id = 500
        almacen.tipo = 500
        #almacen.cuenta_contable = 500
        #almacen.save
        self.assertRaises(IntegrityError)
     '''

    # Si la voy a manejar en este nivel
    def uf_invalida(self):
        # No se arrojaria un error pero ante el evento de una ubicacion fisica inexistente, el valor arrojado por la funcion deberia ser falso
        ubicacionfisica_id = 999
        almacen = Almacen.get(ubicacionfisica_id)
        self.assertFalse(almacen)

    ''' Esta es una validacion algo redundante
    def valor_nonumerico(self):
        # Para asegurarse que el sistema pase el dato en el formato adecuado, solo se permitirian
        ubicacionfisica_id = "999"
        almacen = Almacen.get(ubicacionfisica_id)
        self.assertRaises(ValueError)
    '''

    def regmaestro_inexistente(self):
        #The current date is: Wed 05/20/2015
        """ Pendiente de implementar este caso de prueba, debido a que aun no existe el objeto de registro maestro """

    def regmaestro_noencontrado(self):
        #The current date is: Wed 05/20/2015
        """ Pendiente de implementar este caso de prueba, debido a que aun no existe el objeto de registro maestro """

    def usuario_noexiste(self):
        #The current date is: Wed 05/20/2015
        """ Pendiente de implementar este caso de prueba, debido a que aun no existe el objeto de usuario """

    def usuario_yaasociado(self):
        #The current date is: Wed 05/20/2015
        """ Pendiente de implementar este caso de prueba, debido a que aun no existe el objeto de usuario """

    def accioninvalida(self):
        #The current date is: Wed 05/20/2015
        """ Pendiente de implementar este caso de prueba, debido a que aun no existe el objeto de usuario """

    def sinsaldo(self):
        #The current date is: Wed 05/20/2015
        """ Aun no lo voy a implementar, falta trabajar sobre la clase de Registro Maestro para que actualice info en RegmaestroUbicacionfisica"""

