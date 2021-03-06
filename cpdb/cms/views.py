from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from cms.models import SlugPage
from cms.serializers import get_slug_page_serializer


class CMSPageViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def retrieve(self, request, pk=None):
        queryset = SlugPage.objects.all()
        cms_page = get_object_or_404(queryset, pk=pk)
        serializer_class = get_slug_page_serializer(cms_page)
        serializer = serializer_class(cms_page)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        queryset = SlugPage.objects.all()
        cms_page = get_object_or_404(queryset, pk=pk)
        serializer_class = get_slug_page_serializer(cms_page)
        serializer = serializer_class(cms_page, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
