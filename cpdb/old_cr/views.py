from copy import deepcopy
from collections import OrderedDict

from elasticsearch_dsl import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.serializers import ValidationError
from django.shortcuts import get_object_or_404

from cr.doc_types import CRDocType
from data.models import Allegation
from old_cr.serializers.cr_response_serializers import (
    AttachmentRequestSerializer, CRSummarySerializer,
    AllegationWithNewDocumentsSerializer, CRRelatedComplaintRequestSerializer,
    CRRelatedComplaintSerializer, CRDesktopSerializer, CRMobileSerializer
)
from es_index.pagination import ESQueryPagination


class NoCategoryError(Exception):
    pass


class NoOfficerError(Exception):
    pass


class OldCRViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        query = CRDocType().search().query('term', crid=pk)
        search_result = query.execute()
        try:
            return Response(CRDesktopSerializer(search_result[0].to_dict()).data)
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['POST'], url_path='request-document')
    def request_document(self, request, pk):
        allegation = get_object_or_404(Allegation, crid=pk)
        data = deepcopy(request.data)
        data['allegation'] = allegation.pk
        serializer = AttachmentRequestSerializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Thanks for subscribing', 'crid': pk})

        except ValidationError as e:
            if e.get_codes() == {'non_field_errors': ['unique']}:
                return Response({'message': 'Email already added', 'crid': pk}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'Please enter a valid email'}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['GET'], url_path='list-by-new-document')
    def allegations_with_new_documents(self, request):
        limit = int(request.GET.get('limit', 40))
        results = Allegation.get_cr_with_new_documents(limit)
        serializer = AllegationWithNewDocumentsSerializer(results, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET'], url_path='complaint-summaries')
    def complaint_summaries(self, request):
        query = CRDocType().search().filter('bool', filter=[
            Q('exists', field='summary'),
            ~Q('term', summary__keyword='')
        ])
        query = query.sort('-incident_date', '-crid')
        results = query[0:40].execute()
        return Response(CRSummarySerializer(results, many=True).data, status=status.HTTP_200_OK)

    @detail_route(methods=['GET'], url_path='related-complaints')
    def related_complaints(self, request, pk):
        allegation = get_object_or_404(Allegation, crid=pk)

        request_serializer = CRRelatedComplaintRequestSerializer(data=request.GET)
        if not request_serializer.is_valid():
            return Response({'message': request_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            query_filter = {
                'geo_distance': {
                    'distance': request_serializer.validated_data['distance'],
                    'point': {
                        'lat': allegation.point.y,
                        'lon': allegation.point.x
                    }
                }
            }

            if request_serializer.validated_data['match'] == 'categories':
                categories = list(filter(None, [
                    obj.category
                    for obj in allegation.officerallegation_set.all()
                ]))
                if len(categories) == 0:
                    raise NoCategoryError()

                query = CRDocType().search().query(
                    'bool',
                    must={
                        'terms': {
                            'category_names': categories
                        }
                    },
                    must_not={
                        'terms': {'crid': [pk]}
                    },
                    filter=query_filter
                )
            elif request_serializer.validated_data['match'] == 'officers':
                officers = list(filter(None, [
                    obj.officer_id
                    for obj in allegation.officerallegation_set.all()
                ]))
                if len(officers) == 0:
                    raise NoOfficerError()

                query = CRDocType().search().query(
                    'bool',
                    must={
                        'nested': {
                            'path': 'coaccused',
                            'query': {
                                'terms': {
                                    'coaccused.id': officers
                                }
                            }
                        }
                    },
                    must_not={
                        'terms': {'crid': [pk]}
                    },
                    filter=query_filter
                )

            paginator = ESQueryPagination()
            paginated_query = paginator.paginate_es_query(query, request)
            related_complaint_serializer = CRRelatedComplaintSerializer(paginated_query, many=True)
            return paginator.get_paginated_response(related_complaint_serializer.data)

        except (NoCategoryError, NoOfficerError, AttributeError):
            return Response(OrderedDict([
                ('count', 0),
                ('next', None),
                ('previous', None),
                ('results', [])
            ]))


class OldCRMobileViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        query = CRDocType().search().query('term', crid=pk)
        search_result = query.execute()
        try:
            return Response(CRMobileSerializer(search_result[0].to_dict()).data)
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['POST'], url_path='request-document')
    def request_document(self, request, pk):
        allegation = get_object_or_404(Allegation, crid=pk)
        data = deepcopy(request.data)
        data['allegation'] = allegation.pk
        serializer = AttachmentRequestSerializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Thanks for subscribing', 'crid': pk})

        except ValidationError as e:
            if e.get_codes() == {'non_field_errors': ['unique']}:
                return Response(
                    {'message': 'Email already added', 'crid': pk},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({'message': 'Please enter a valid email'}, status=status.HTTP_400_BAD_REQUEST)