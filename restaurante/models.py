# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models

from restaurante.utils.PostgreSQL_DjangoUtils import pgSQL_Utils

class AgrupadorAltonivel(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_agrupadorbajonivel = models.IntegerField(db_column='Id_AgrupadorBajoNivel', blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=255, blank=True)  # Field name made lowercase.
    precio = models.DecimalField(db_column='Precio', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    inventariable = models.NullBooleanField(db_column='Inventariable')  # Field name made lowercase.
    subpreparacion = models.NullBooleanField(db_column='Subpreparacion')  # Field name made lowercase.
    id_ubicacionfisica = models.IntegerField(db_column='Id_UbicacionFisica', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Agrupador_AltoNivel'


class AgrupadorBajonivel(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_registromaestro = models.IntegerField(db_column='Id_RegistroMaestro', blank=True, null=True)  # Field name made lowercase.
    cantidad = models.CharField(db_column='Cantidad', max_length=255, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Agrupador_BajoNivel'


class AsientoContable(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombreclasificacion = models.CharField(db_column='NombreClasificacion', max_length=255, blank=True)  # Field name made lowercase.
    nombreasiento = models.CharField(db_column='NombreAsiento', max_length=255, blank=True)  # Field name made lowercase.
    id_subcuentacontablecargo = models.IntegerField(db_column='ID_SubcuentaContableCargo', blank=True, null=True)  # Field name made lowercase.
    id_subcuentacontableabono = models.IntegerField(db_column='ID_SubcuentaContableAbono', blank=True, null=True)  # Field name made lowercase.
    montocalculado = models.NullBooleanField(db_column='MontoCalculado')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Asiento_Contable'


class CatalogoClasificacion(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombreclasificacion = models.CharField(db_column='NombreClasificacion', max_length=255, blank=True)  # Field name made lowercase.
    estatus = models.CharField(db_column='Estatus', max_length=255, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Catalogo_Clasificacion'


class ClaveFolio(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombredocumento = models.CharField(db_column='NombreDocumento', max_length=255, blank=True)  # Field name made lowercase.
    clavefolio = models.CharField(db_column='ClaveFolio', max_length=255, blank=True)  # Field name made lowercase.
    id_clientesistema = models.IntegerField(db_column='Id_ClienteSistema', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True 
        db_table = 'Clave_Folio'

    def _str_(self):
        return ' '.join([self.nombredocumento, self.clavefolio,])


class ClienteSistema(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_personafiscal = models.IntegerField(db_column='Id_PersonaFiscal', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Cliente_Sistema'


class CuentaBancaria(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombrebanco = models.CharField(db_column='NombreBanco', max_length=255, blank=True)  # Field name made lowercase.
    tipocuenta = models.CharField(db_column='TipoCuenta', max_length=255, blank=True)  # Field name made lowercase.
    moneda = models.CharField(db_column='Moneda', max_length=255, blank=True)  # Field name made lowercase.
    id_subcuentacontable = models.IntegerField(db_column='ID_SubcuentaContable', blank=True, null=True)  # Field name made lowercase.
    saldo = models.IntegerField(db_column='Saldo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Cuenta_Bancaria'


class CuentaContable(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255, blank=True)  # Field name made lowercase.
    tipo = models.IntegerField(db_column='Tipo', blank=True)  # Field name made lowercase.
    id_cliente = models.IntegerField(db_column='Id_Cliente', blank=True, null=True)  # Field name made lowercase.
    sub_tipo = models.CharField(db_column='Sub_Tipo', max_length=1, blank=True, null=True)  # Field name made lowercase.
    id_subcuentacontable = models.IntegerField(db_column='Id_Subcuentacontable', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Cuenta_Contable'

    def save(self, *args, **kwargs):
        if not self.id:
            pid = pgSQL_Utils()
            self.id = pid.prefetch_id(self)
        super(CuentaContable, self).save(*args, **kwargs)


class DetalleDocumento(models.Model):
    id_documento = models.IntegerField(db_column='Id_Documento', blank=True, null=True)  # Field name made lowercase.
    id_registromaestro = models.IntegerField(db_column='Id_RegistroMaestro', blank=True, null=True)  # Field name made lowercase.
    id_personafiscal = models.IntegerField(db_column='Id_PersonaFiscal', blank=True, null=True)  # Field name made lowercase.
    id_ubicacionfisica1 = models.IntegerField(db_column='Id_UbicacionFisica1', blank=True, null=True)  # Field name made lowercase.
    id_ubicacionfisica2 = models.IntegerField(db_column='Id_UbicacionFisica2', blank=True, null=True)  # Field name made lowercase.
    subtotal = models.IntegerField(db_column='Subtotal', blank=True, null=True)  # Field name made lowercase.
    comentarios = models.CharField(db_column='Comentarios', max_length=255, blank=True)  # Field name made lowercase.
    estatus = models.CharField(db_column='Estatus', max_length=255, blank=True)  # Field name made lowercase.
    id_cuentabancaria1 = models.IntegerField(db_column='Id_CuentaBancaria1', blank=True, null=True)  # Field name made lowercase.
    id_cuentabancaria2 = models.IntegerField(db_column='Id_CuentaBancaria2', blank=True, null=True)  # Field name made lowercase.
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Detalle_Documento'


class DetalleUbicacion(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_ubicacionfisica = models.IntegerField(db_column='ID_UbicacionFisica', blank=True, null=True)  # Field name made lowercase.
    direccion = models.TextField(db_column='Direccion', blank=True)  # Field name made lowercase.
    telefono = models.CharField(db_column='Telefono', max_length=255, blank=True)  # Field name made lowercase.
    horariorecepcion = models.CharField(db_column='HorarioRecepcion', max_length=255, blank=True)  # Field name made lowercase.
    saldoactual = models.IntegerField(db_column='SaldoActual', blank=True, null=True)  # Field name made lowercase.
    impresora = models.CharField(db_column='Impresora', max_length=255, blank=True)  # Field name made lowercase.
    terminalsalida = models.CharField(db_column='TerminalSalida', max_length=255, blank=True)  # Field name made lowercase.
    minimocomensales = models.CharField(db_column='MinimoComensales', max_length=255, blank=True)  # Field name made lowercase.
    maximocomensales = models.CharField(db_column='MaximoComensales', max_length=255, blank=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=255, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Detalle_Ubicacion'

    def save(self, *args, **kwargs):
        if not self.id:
            pid = pgSQL_Utils()
            self.id = pid.prefetch_id(self)
        super(DetalleUbicacion, self).save(*args, **kwargs)

class Documento(models.Model):
    fecha_hora = models.DateTimeField(db_column='Fecha/Hora', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    id_clavefolio = models.IntegerField(db_column='Id_ClaveFolio', blank=True, null=True)  # Field name made lowercase.
    id_usuario = models.IntegerField(db_column='Id_Usuario', blank=True, null=True)  # Field name made lowercase.
    monto = models.IntegerField(db_column='Monto', blank=True, null=True)  # Field name made lowercase.
    id_documentoorigen = models.IntegerField(db_column='Id_DocumentoOrigen', blank=True, null=True)  # Field name made lowercase.
    id_conceptodocumento = models.IntegerField(db_column='Id_ConceptoDocumento', blank=True, null=True)  # Field name made lowercase.
    foliointerno = models.CharField(db_column='FolioInterno', max_length=255, blank=True)  # Field name made lowercase.
    estatus = models.CharField(db_column='Estatus', max_length=255, blank=True)  # Field name made lowercase.
    id_documentomovimiento = models.IntegerField(db_column='Id_DocumentoMovimiento', blank=True, null=True)  # Field name made lowercase.
    foliodocumento = models.CharField(db_column='FolioDocumento', max_length=255, blank=True)  # Field name made lowercase.
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_subcuentacontableabono = models.IntegerField(db_column='ID_SubcuentaContableAbono', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Documento'


class DocumentoAsiento(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_clavefolio = models.IntegerField(db_column='Id_ClaveFolio', blank=True, null=True)  # Field name made lowercase.
    id_conceptodocumento = models.IntegerField(db_column='Id_ConceptoDocumento', blank=True, null=True)  # Field name made lowercase.
    id_movimientodocumento = models.IntegerField(db_column='Id_MovimientoDocumento', blank=True, null=True)  # Field name made lowercase.
    id_asiento = models.IntegerField(db_column='Id_Asiento', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Documento_Asiento'


class DocumentoConcepto(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    conceptodocumento = models.CharField(db_column='ConceptoDocumento', max_length=255, blank=True)  # Field name made lowercase.
    id_subcuentacontablecargo = models.IntegerField(db_column='ID_SubcuentaContableCargo', blank=True, null=True)  # Field name made lowercase.
    id_clavefolio = models.IntegerField(db_column='Id_ClaveFolio', blank=True, null=True)  # Field name made lowercase.
    id_movimiento = models.IntegerField(db_column='Id_Movimiento', blank=True, null=True)  # Field name made lowercase.
    id_subcuentacontableabono = models.IntegerField(db_column='ID_SubcuentaContableAbono', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Documento_Concepto'


class DocumentoMovimiento(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    movimientodocumento = models.CharField(db_column='MovimientoDocumento', max_length=255, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Documento_Movimiento'


class Empleado(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.TextField(db_column='Nombre', blank=True)  # Field name made lowercase.
    direccion = models.TextField(db_column='Direccion', blank=True)  # Field name made lowercase.
    telefono1 = models.CharField(db_column='Telefono1', max_length=255, blank=True)  # Field name made lowercase.
    telefono2 = models.CharField(db_column='Telefono2', max_length=255, blank=True)  # Field name made lowercase.
    telefono3 = models.CharField(db_column='Telefono3', max_length=255, blank=True)  # Field name made lowercase.
    correoelectronico = models.CharField(db_column='CorreoElectronico', max_length=255, blank=True)  # Field name made lowercase.
    puesto = models.CharField(db_column='Puesto', max_length=255, blank=True)  # Field name made lowercase.
    id_sucursal_sistema = models.IntegerField(db_column='Id_Sucursal_Sistema', blank=True, null=True)  # Field name made lowercase.
    estatus = models.CharField(db_column='Estatus', max_length=255, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Empleado'


class ExtradetalleDocumento(models.Model):
    id_detalledocumento = models.IntegerField(db_column='Id_DetalleDocumento', blank=True, null=True)  # Field name made lowercase.
    numerocomensales = models.IntegerField(db_column='NumeroComensales', blank=True, null=True)  # Field name made lowercase.
    id_presentacion = models.IntegerField(db_column='Id_Presentacion', blank=True, null=True)  # Field name made lowercase.
    cantidad = models.IntegerField(db_column='Cantidad', blank=True, null=True)  # Field name made lowercase.
    costopreciounitario = models.IntegerField(db_column='CostoPrecioUnitario', blank=True, null=True)  # Field name made lowercase.
    costopreciototal = models.IntegerField(db_column='CostoPrecioTotal', blank=True, null=True)  # Field name made lowercase.
    cantidadsurtida = models.IntegerField(db_column='CantidadSurtida', blank=True, null=True)  # Field name made lowercase.
    fechahoraapertura = models.DateTimeField(db_column='FechaHoraApertura', blank=True, null=True)  # Field name made lowercase.
    fechahoracierre = models.DateTimeField(db_column='FechaHoraCierre', blank=True, null=True)  # Field name made lowercase.
    saldoapertura = models.IntegerField(db_column='SaldoApertura', blank=True, null=True)  # Field name made lowercase.
    saldocierre = models.IntegerField(db_column='SaldoCierre', blank=True, null=True)  # Field name made lowercase.
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ExtraDetalle_Documento'


class GrupoUsuario(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_perfilacceso = models.IntegerField(db_column='Id_PerfilAcceso', blank=True, null=True)  # Field name made lowercase.
    id_usuario = models.IntegerField(db_column='Id_Usuario', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Grupo_Usuario'


class LibroContable(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    periodo = models.CharField(db_column='Periodo', max_length=255, blank=True)  # Field name made lowercase.
    anno = models.IntegerField(db_column='Anno', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Libro_Contable'


class LibroCuentacontable(models.Model):
    saldo = models.IntegerField(db_column='Saldo', blank=True, null=True)  # Field name made lowercase.
    id_librosucursal = models.IntegerField(db_column='ID_LibroSucursal', blank=True, null=True)  # Field name made lowercase.
    id_cuentacontable = models.IntegerField(db_column='ID_CuentaContable', blank=True, null=True)  # Field name made lowercase.
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Libro_CuentaContable'


class LibroSucursal(models.Model):
    estatus = models.CharField(db_column='Estatus', max_length=255, blank=True)  # Field name made lowercase.
    id_sucursal = models.IntegerField(db_column='ID_Sucursal', blank=True, null=True)  # Field name made lowercase.
    id_librocontable = models.IntegerField(db_column='ID_LibroContable', blank=True, null=True)  # Field name made lowercase.
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Libro_Sucursal'


class MontoCalculado(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombremontocalculado = models.CharField(db_column='NombreMontoCalculado', max_length=255, blank=True)  # Field name made lowercase.
    montofijo = models.DecimalField(db_column='MontoFijo', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    porcentajeoperacion = models.IntegerField(db_column='PorcentajeOperacion', blank=True, null=True)  # Field name made lowercase.
    causaimpuesto = models.NullBooleanField(db_column='CausaImpuesto')  # Field name made lowercase.
    requiereautorizacion = models.NullBooleanField(db_column='RequiereAutorizacion')  # Field name made lowercase.
    id_asientocontable = models.IntegerField(db_column='Id_AsientoContable', blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=255, blank=True)  # Field name made lowercase.
    estatus = models.CharField(db_column='Estatus', max_length=255, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Monto_Calculado'


class MontoCalculadoDetalle(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_montocalculado = models.IntegerField(db_column='Id_MontoCalculado', blank=True, null=True)  # Field name made lowercase.
    id_detalledocumento = models.IntegerField(db_column='Id_DetalleDocumento', blank=True, null=True)  # Field name made lowercase.
    monto = models.IntegerField(db_column='Monto', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Monto_Calculado_Detalle'


class MontoCalculadoDocumento(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_montocalculado = models.IntegerField(db_column='Id_MontoCalculado', blank=True, null=True)  # Field name made lowercase.
    id_documento = models.IntegerField(db_column='Id_Documento', blank=True, null=True)  # Field name made lowercase.
    monto = models.IntegerField(db_column='Monto', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Monto_Calculado_Documento'


class MovimientoContable(models.Model):
    id_librosucursal = models.IntegerField(db_column='ID_LibroSucursal', blank=True, null=True)  # Field name made lowercase.
    id_documento = models.IntegerField(db_column='ID_Documento', blank=True, null=True)  # Field name made lowercase.
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_documentoconcepto = models.IntegerField(db_column='ID_DocumentoConcepto', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Movimiento_Contable'


class NumeracionFolio(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_clavefolio = models.IntegerField(db_column='Id_ClaveFolio', blank=True, null=True)  # Field name made lowercase.
    id_sucursal_sistema = models.IntegerField(db_column='Id_Sucursal_Sistema', blank=True, null=True)  # Field name made lowercase.
    numeroinicial = models.IntegerField(db_column='NumeroInicial', blank=True, null=True)  # Field name made lowercase.
    numerofinal = models.IntegerField(db_column='NumeroFinal', blank=True, null=True)  # Field name made lowercase.
    numeroactual = models.IntegerField(db_column='NumeroActual', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Numeracion_Folio'


class PerfilimpuestoMontocalculado(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_perfilimpuesto = models.IntegerField(db_column='Id_PerfilImpuesto', blank=True, null=True)  # Field name made lowercase.
    id_montocalculado = models.IntegerField(db_column='Id_MontoCalculado', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PerfilImpuesto_MontoCalculado'


class PerfilAcceso(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombreperfil = models.CharField(db_column='NombrePerfil', max_length=255, blank=True)  # Field name made lowercase.
    perfiltoken = models.TextField(db_column='PerfilToken', blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Perfil_Acceso'


class PerfilImpuesto(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombreperfilimpuesto = models.CharField(db_column='NombrePerfilImpuesto', max_length=255, blank=True)  # Field name made lowercase.
    estatus = models.CharField(db_column='Estatus', max_length=255, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Perfil_Impuesto'


class PersonafiscalProveedor(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_personafiscal = models.IntegerField(db_column='Id_PersonaFiscal', blank=True, null=True)  # Field name made lowercase.
    diascredito = models.IntegerField(db_column='DiasCredito', blank=True, null=True)  # Field name made lowercase.
    tiemposurtido = models.IntegerField(db_column='TiempoSurtido', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PersonaFiscal_Proveedor'


class PersonaFiscal(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.TextField(db_column='Nombre', blank=True)  # Field name made lowercase.
    direccion = models.TextField(db_column='Direccion', blank=True)  # Field name made lowercase.
    telefono1 = models.CharField(db_column='Telefono1', max_length=255, blank=True)  # Field name made lowercase.
    telefono2 = models.CharField(db_column='Telefono2', max_length=255, blank=True)  # Field name made lowercase.
    telefono3 = models.CharField(db_column='Telefono3', max_length=255, blank=True)  # Field name made lowercase.
    correoelectronico = models.CharField(db_column='CorreoElectronico', max_length=255, blank=True)  # Field name made lowercase.
    personacontacto = models.CharField(db_column='PersonaContacto', max_length=255, blank=True)  # Field name made lowercase.
    raz_n_social = models.TextField(db_column='Raz\xf3n Social', blank=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    rfc = models.CharField(db_column='RFC', max_length=255, blank=True)  # Field name made lowercase.
    domiciliofiscal = models.CharField(db_column='DomicilioFiscal', max_length=255, blank=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=255, blank=True)  # Field name made lowercase.
    estatus = models.CharField(db_column='Estatus', max_length=255, blank=True)  # Field name made lowercase.
    fechanacimiento = models.DateTimeField(db_column='FechaNacimiento', blank=True, null=True)  # Field name made lowercase.
    fechaaniversario = models.DateTimeField(db_column='FechaAniversario', blank=True, null=True)  # Field name made lowercase.
    cuentabancaria1 = models.CharField(db_column='CuentaBancaria1', max_length=255, blank=True)  # Field name made lowercase.
    banco1 = models.CharField(db_column='Banco1', max_length=255, blank=True)  # Field name made lowercase.
    cuentabancaria2 = models.CharField(db_column='CuentaBancaria2', max_length=255, blank=True)  # Field name made lowercase.
    banco2 = models.CharField(db_column='Banco2', max_length=255, blank=True)  # Field name made lowercase.
    cuentabancaria3 = models.CharField(db_column='CuentaBancaria3', max_length=255, blank=True)  # Field name made lowercase.
    banco3 = models.CharField(db_column='Banco3', max_length=255, blank=True)  # Field name made lowercase.
    cuenta_contable = models.IntegerField(db_column='Cuenta_Contable', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Persona_Fiscal'


class Presentacion(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombrepresentacion = models.CharField(db_column='NombrePresentacion', max_length=255, blank=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=255, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Presentacion'


class ProveedorRegmaestrocompra(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=255)  # Field name made lowercase.
    id_personafiscalproveedor = models.IntegerField(db_column='Id_PersonaFiscalProveedor', blank=True, null=True)  # Field name made lowercase.
    id_registromaestrocompra = models.IntegerField(db_column='Id_RegistroMaestroCompra', blank=True, null=True)  # Field name made lowercase.
    id_documentoultimo = models.IntegerField(db_column='Id_DocumentoUltimo', blank=True, null=True)  # Field name made lowercase.
    precioultimo = models.IntegerField(db_column='PrecioUltimo', blank=True, null=True)  # Field name made lowercase.
    proveedorpreferido = models.NullBooleanField(db_column='ProveedorPreferido')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Proveedor_RegMaestroCompra'


class RegmaestroCompra(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_registromaestro = models.IntegerField(db_column='Id_RegistroMaestro', blank=True, null=True)  # Field name made lowercase.
    id_presentacioncompra = models.IntegerField(db_column='Id_PresentacionCompra', blank=True, null=True)  # Field name made lowercase.
    id_presentacioninventario = models.IntegerField(db_column='Id_PresentacionInventario', blank=True, null=True)  # Field name made lowercase.
    equivalenciaentrepresentacion = models.IntegerField(db_column='EquivalenciaEntrePresentacion', blank=True, null=True)  # Field name made lowercase.
    id_unidadmedida = models.IntegerField(db_column='Id_UnidadMedida', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RegMaestro_Compra'


class RegmaestroContabilidad(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_perfilimpuesto = models.IntegerField(db_column='Id_PerfilImpuesto', blank=True, null=True)  # Field name made lowercase.
    id_registromaestro = models.IntegerField(db_column='Id_RegistroMaestro', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RegMaestro_Contabilidad'


class RegmaestroFoto(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_registromaestro = models.IntegerField(db_column='Id_RegistroMaestro', blank=True, null=True)  # Field name made lowercase.
    path_foto = models.TextField(db_column='Path_Foto', blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RegMaestro_Foto'


class RegmaestroInventario(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_registromaestro = models.IntegerField(db_column='Id_RegistroMaestro', blank=True, null=True)  # Field name made lowercase.
    id_presentacioninventario = models.IntegerField(db_column='Id_PresentacionInventario', blank=True, null=True)  # Field name made lowercase.
    inventarioseguridad = models.IntegerField(db_column='InventarioSeguridad', blank=True, null=True)  # Field name made lowercase.
    caducidad = models.IntegerField(db_column='Caducidad', blank=True, null=True)  # Field name made lowercase.
    localidad = models.CharField(db_column='Localidad', max_length=255, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RegMaestro_Inventario'


class RegmaestroPedimento(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_registromaestro = models.IntegerField(db_column='Id_RegistroMaestro', blank=True, null=True)  # Field name made lowercase.
    tamanominimolote = models.IntegerField(db_column='TamanoMinimoLote', blank=True, null=True)  # Field name made lowercase.
    existenciasrequeridas = models.IntegerField(db_column='ExistenciasRequeridas', blank=True, null=True)  # Field name made lowercase.
    plancompra = models.NullBooleanField(db_column='PlanCompra')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RegMaestro_Pedimento'


class RegmaestroUbicacionfisica(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_registromaestro = models.IntegerField(db_column='Id_RegistroMaestro', blank=True, null=True)  # Field name made lowercase.
    id_ubicacionfisica = models.IntegerField(db_column='Id_UbicacionFisica', blank=True, null=True)  # Field name made lowercase.
    existencias = models.IntegerField(db_column='Existencias', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RegMaestro_UbicacionFisica'


class RegmaestroVenta(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_registromaestro = models.IntegerField(db_column='Id_RegistroMaestro', blank=True, null=True)  # Field name made lowercase.
    id_presentacioninventario = models.IntegerField(db_column='Id_PresentacionInventario', blank=True, null=True)  # Field name made lowercase.
    id_presentacionconsumo = models.IntegerField(db_column='Id_PresentacionConsumo', blank=True, null=True)  # Field name made lowercase.
    equivalenciaentrepresentaciones = models.IntegerField(db_column='EquivalenciaEntrePresentaciones', blank=True, null=True)  # Field name made lowercase.
    id_unidadmedida = models.IntegerField(db_column='Id_UnidadMedida', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RegMaestro_Venta'


class RegistroMaestro(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255, blank=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=255, blank=True)  # Field name made lowercase.
    id_clasificacion = models.IntegerField(db_column='Id_Clasificacion', blank=True, null=True)  # Field name made lowercase.
    marca = models.CharField(db_column='Marca', max_length=255, blank=True)  # Field name made lowercase.
    estatus = models.CharField(db_column='Estatus', max_length=255, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Registro_Maestro'


class SucursalSistema(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.TextField(db_column='Nombre', blank=True)  # Field name made lowercase.
    direccion = models.TextField(db_column='Direccion', blank=True)  # Field name made lowercase.
    personacontacto = models.CharField(db_column='PersonaContacto', max_length=255, blank=True)  # Field name made lowercase.
    telefono1 = models.CharField(db_column='Telefono1', max_length=255, blank=True)  # Field name made lowercase.
    telefono2 = models.CharField(db_column='Telefono2', max_length=255, blank=True)  # Field name made lowercase.
    telefono3 = models.CharField(db_column='Telefono3', max_length=255, blank=True)  # Field name made lowercase.
    correoelectronico = models.CharField(db_column='CorreoElectronico', max_length=255, blank=True)  # Field name made lowercase.
    id_cliente = models.IntegerField(db_column='ID_Cliente', blank=True, null=True)  # Field name made lowercase.
    identificadorcorto = models.CharField(db_column='IdentificadorCorto', max_length=3, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Sucursal_Sistema'


class UbicacionFisica(models.Model):
    #id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id = models.AutoField(db_column='ID', primary_key=True)
    id_sucursalsistema = models.IntegerField(db_column='Id_SucursalSistema', blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255, blank=True)  # Field name made lowercase.
    descripcion = models.TextField(db_column='Descripcion', blank=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=255, blank=True)  # Field name made lowercase.
    id_subcuentacontable = models.IntegerField(db_column='Id_SubCuentaContable', blank=True, null=True)  # Field name made lowercase.
    estatus = models.CharField(db_column='Estatus', max_length=255, blank=True)  # Field name made lowercase.
    cuenta_contable = models.IntegerField(db_column='Cuenta_Contable', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Ubicacion_Fisica'

    def save(self, *args, **kwargs):
        if not self.id:
            pid = pgSQL_Utils()
            self.id = pid.prefetch_id(self)
        super(UbicacionFisica, self).save(*args, **kwargs)


class UnidadMedida(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    unidadmedida = models.CharField(db_column='UnidadMedida', max_length=255, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Unidad_Medida'


class Usuario(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_empleado = models.IntegerField(db_column='Id_Empleado', blank=True, null=True)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=255, blank=True)  # Field name made lowercase.
    estatus = models.CharField(db_column='Estatus', max_length=255, blank=True)  # Field name made lowercase.
    id_ubicacionfisica = models.IntegerField(db_column='Id_UbicacionFisica', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Usuario'


class UsuarioSesion(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_usuario = models.IntegerField(db_column='Id_Usuario', blank=True, null=True)  # Field name made lowercase.
    id_sucursal = models.IntegerField(db_column='Id_Sucursal', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Usuario_Sesion'


class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'


class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'


class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'


class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'


class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', blank=True, null=True)
    user = models.ForeignKey(AuthUser)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'


class DjangoMigrations(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'

class AuthUser_UbicacionFisica(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser)
    ubicacionfisica = models.ForeignKey(UbicacionFisica)

    class Meta:
        managed = False
        db_table = 'AuthUser_UbicacionFisica'
