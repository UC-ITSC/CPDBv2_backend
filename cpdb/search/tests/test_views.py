from mock import patch

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from data.factories import OfficerFactory, OfficerHistoryFactory, PoliceUnitFactory
from search.tests.utils import IndexMixin


class SearchV1ViewSetTestCase(IndexMixin, APITestCase):
    @patch('search.views.SearchManager.search')
    def test_retrieve_ok(self, search):
        text = 'any_text'
        search.return_value = 'anything_suggester_returns'

        url = reverse('api:suggestion-detail', kwargs={
            'text': text
        })
        response = self.client.get(url, {
            'contentType': 'OFFICER'
        })

        expect(response.status_code).to.equal(status.HTTP_200_OK)
        expect(response.data).to.equal('anything_suggester_returns')
        search.assert_called_with(text, content_type='OFFICER')

    def test_search_unit_officer(self):
        officer = OfficerFactory()
        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(unit_name='123'))

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-detail', kwargs={
            'text': 12
        })
        response = self.client.get(url)

        results = response.data['UNIT > OFFICERS']
        expect(results).to.have.length(1)

        expect(results[0]['text']).to.eq(officer.full_name)


class SearchV2ViewSetTestCase(APITestCase):
    @patch('search.views.SearchManager.search')
    def test_retrieve_ok(self, search):
        text = 'any_text'
        search.return_value = 'anything_suggester_returns'

        url = reverse('api-v2:search-detail', kwargs={
            'text': text
        })
        response = self.client.get(url, {
            'contentType': 'OFFICER'
        })

        expect(response.status_code).to.equal(status.HTTP_200_OK)
        expect(response.data).to.equal('anything_suggester_returns')
        search.assert_called_with(text, content_type='OFFICER')
