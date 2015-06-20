from restaurante.repository.AreaPreparacion_repository import AreaPreparacion

class Almacen(AreaPreparacion):

    def save(self):
        super(Almacen, self).save()

    def disable(self):
        super(Almacen, self).disable()

    def get(self, id_ubicacionfisica):
        super(Almacen, self).get(id_ubicacionfisica)

    def get_stock(self, registromaestro):
        super(Almacen, self).get_stock(registromaestro)