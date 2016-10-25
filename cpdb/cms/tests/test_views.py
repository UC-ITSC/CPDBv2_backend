from django.core.urlresolvers import reverse

from freezegun import freeze_time
from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from authentication.factories import AdminUserFactory
from cms.cms_page_descriptors import LandingPageDescriptor, ReportPageDescriptor
from cms.models import ReportPage, SlugPage


class CMSPageViewSetTestCase(APITestCase):
    @freeze_time('2016-10-07')
    def setUp(self):
        with patch('cms.cms_fields.generate_draft_block_key', return_value='abc12'):
            self.landing_page_descriptor = LandingPageDescriptor()
            self.landing_page_descriptor.seed_data()
        self.landing_page_descriptor.update({'fields': [{
            'name': 'vftg_link',
            'type': 'link',
            'value': 'https://google.com'
            }]})
        self.maxDiff = None

    def test_update_landing_page(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        url = reverse('api-v2:cms-page-detail', kwargs={'pk': 'landing-page'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'fields': [
            {
                'name': 'collaborate_header',
                'type': 'plain_text',
                'value': 'Collaborate With Us.'
            }
        ]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['fields']), 12)
        response_data = {
            field['name']: field for field in response.data['fields']
        }
        self.assertEqual(
            response_data['collaborate_header']['value'],
            'Collaborate With Us.')

        self.assertEqual(
            SlugPage.objects.first().fields['collaborate_header_value'],
            'Collaborate With Us.')

    def test_get_landing_page(self):
        url = reverse('api-v2:cms-page-detail', kwargs={'pk': 'landing-page'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['fields']), 12)
        response_data = {
            field['name']: field for field in response.data['fields']
        }
        self.assertEqual(
            response_data['reporting_header'],
            {
                'name': 'reporting_header',
                'type': 'plain_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'Recent Reports',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['reporting_randomizer'],
            {
                'name': 'reporting_randomizer',
                'type': 'randomizer',
                'value': {
                    'poolSize': 10,
                    'selectedStrategyId': 1,
                    'strategies': [
                        {
                            'id': 1,
                            'name': 'Last entries'
                        },
                        {
                            'id': 2,
                            'name': 'Last days'
                        }
                    ]
                }
            })
        self.assertEqual(
            response_data['faq_header'],
            {
                'name': 'faq_header',
                'type': 'plain_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'FAQ',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['faq_randomizer'],
            {
                'name': 'faq_randomizer',
                'type': 'randomizer',
                'value': {
                    'poolSize': 10,
                    'selectedStrategyId': 1,
                    'strategies': [
                        {
                            'id': 1,
                            'name': 'Last entries'
                        },
                        {
                            'id': 2,
                            'name': 'Last days'
                        }
                    ]
                }
            })
        self.assertEqual(
            response_data['vftg_date'],
            {
                'name': 'vftg_date',
                'type': 'date',
                'value': '2016-10-07'
            })
        self.assertEqual(
            response_data['vftg_link'],
            {
                'name': 'vftg_link',
                'type': 'link',
                'value': 'https://google.com'
            })
        self.assertEqual(
            response_data['vftg_content'],
            {
                'name': 'vftg_content',
                'type': 'plain_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'Real Independence for Police Oversight Agencies',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['collaborate_header'],
            {
                'name': 'collaborate_header',
                'type': 'plain_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'Collaborate',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['collaborate_content'],
            {
                'name': 'collaborate_content',
                'type': 'multiline_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': (
                                'We are collecting and publishing information that sheds light on police misconduct.'),
                            'type': 'unstyled'
                        },
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': (
                                'If you have documents or datasets you would like to publish, '
                                'please email us, or learn more.'),
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['about_header'],
            {
                'name': 'about_header',
                'type': 'plain_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'About',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['about_content'],
            {
                'name': 'about_content',
                'type': 'multiline_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': (
                                'The Citizens Police Data Project houses police disciplinary '
                                'information obtained from the City of Chicago.'),
                            'type': 'unstyled'
                        },
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': (
                                'The information and stories we have collected here are intended as a resource for '
                                'public oversight. Our aim is to create a new model of accountability between '
                                'officers and citizens.'),
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })


class ReportPageViewSetTestCase(APITestCase):
    def setUp(self):
        with patch('cms.cms_fields.generate_draft_block_key', return_value='abc12'):
            rp_descriptor = ReportPageDescriptor()
            rp_descriptor.seed_data()
        self.maxDiff = None

    def test_list_report_page(self):
        url = reverse('api-v2:report-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        [report] = ReportPage.objects.all()
        actual_data = dict(response.data)
        actual_results = actual_data['results']

        self.assertEqual(actual_data['count'], 1)
        self.assertEqual(actual_data['next'], None)
        self.assertEqual(actual_data['previous'], None)

        self.assertDictEqual(actual_results[0], {
            'fields': [
                {
                    'name': field,
                    'type': report.fields['%s_type' % field],
                    'value': report.fields['%s_value' % field],
                }
                for field in ['author', 'excerpt', 'publication', 'publish_date', 'title']
            ],
            'id': report.id
        })

    def test_update_report_page(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        report_page = ReportPage.objects.first()

        url = reverse('api-v2:report-detail', kwargs={'pk': report_page.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'fields': [
            {
                'name': 'title',
                'type': 'plain_text',
                'value': 'new title'
            }
        ]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['fields']), 5)
        response_data = {
            field['name']: field for field in response.data['fields']
        }
        self.assertEqual(
            response_data['title']['value'],
            'new title')
        report_page.refresh_from_db()
        self.assertEqual(
            report_page.fields['title_value'],
            'new title')
