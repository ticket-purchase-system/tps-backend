class BaseRepository:
    model = None

    def get_by_id(self, id):
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None

    def get_all(self):
        return self.model.objects.all()

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        instance.save()
        return instance

    def update(self, instance, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(instance, key, value)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()