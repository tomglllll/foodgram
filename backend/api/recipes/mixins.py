from rest_framework import mixins, viewsets


class ListRetrieveGenericMixin(mixins.ListModelMixin,
                               mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    pass
