''' Clase con metodos de funcionalidad adicional entre Django y PostgreSQL que no son soportadas por el modelo '''

import os
from django.db import connection, models, DatabaseError

class pgSQL_Utils():

    def prefetch_id(self, instance):
        """ Fetch the next value in a django id autofield postgresql sequence """
        cursor = connection.cursor()
        sql ="select nextval('\"{0}_ID_seq\"'::regclass)".format(instance._meta.db_table)
        #cursor.execute(
        # "select currval('""{0}_ID_seq""'::regclass)".format(
        #"SELECT nextval('{0}_{1}_id_seq'::regclass)".format( #Revisar este query ya que quizas sea necesario adaptarlo
        #    instance._meta.db_table
        #    )
        try:
            cursor.execute(sql)
        except DatabaseError as e:
            #Lo recomendable es cachar la excepcion y llamar una funcion para propagarla mas arriba
            print ("Existe un error al tratar de generar el id del objeto %err", e.pgcode)
        #)
        row = cursor.fetchone()
        cursor.close()
        return int(row[0])

''' Probar si es posible incluir dentro de cada clase del modelo el siguiente codigo a fin de sobrecargar el metodo save 

class SomeModel(models.Model):

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = prefetch_id(instance)
        
        super(SomeModel, self).save(*args, **kwargs)

Sino seria necesario incluir la condicion dentro de las clases del repositorio

'''
