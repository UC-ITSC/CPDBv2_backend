from datetime import date, datetime
from decimal import Decimal

from django.contrib.gis.geos import Point
from django.test import SimpleTestCase, TestCase, override_settings

from mock import Mock, patch
from robber import expect
import pytz

from data.constants import MEDIA_TYPE_DOCUMENT
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, OfficerHistoryFactory,
    AllegationCategoryFactory, VictimFactory, AwardFactory, AttachmentFileFactory,
    SalaryFactory, OfficerBadgeNumberFactory, ComplainantFactory
)
from officers.tests.utils import validate_object
from officers.indexers import (
    OfficersIndexer,
    OfficerPercentileIndexer,
    CRNewTimelineEventIndexer,
    CRNewTimelineEventPartialIndexer,
    UnitChangeNewTimelineEventIndexer,
    JoinedNewTimelineEventIndexer,
    TRRNewTimelineEventIndexer,
    AwardNewTimelineEventIndexer,
    OfficerCoaccusalsIndexer,
    RankChangeNewTimelineEventIndexer,
)
from trr.factories import TRRFactory
from officers.doc_types import OfficerNewTimelineEventDocType
from officers.index_aliases import officers_index_alias


class OfficersIndexerTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None

    def extract_data(self):
        indexer = OfficersIndexer()
        return [indexer.extract_datum(obj) for obj in indexer.get_query()]

    @override_settings(V1_URL='http://test.com')
    @patch(
        'officers.indexers.officer_percentile.top_percentile',
        Mock(return_value=Mock(values=Mock(return_value=[])))
    )
    def test_extract_info(self):
        officer = OfficerFactory(
            id=123,
            first_name='Alex',
            last_name='Mack',
            rank='5',
            race='White',
            gender='M',
            appointed_date=date(2017, 2, 27),
            resignation_date=date(2017, 12, 27),
            active='Yes',
            birth_year=1910,
            complaint_percentile=99.8,
            honorable_mention_percentile=98,
            tags=['Jason VanDyke']
        )
        TRRFactory(officer=officer)
        SalaryFactory(officer=officer, salary=9000)
        AwardFactory(
            officer=officer,
            award_type='Honorable Mention'
        )
        AwardFactory(
            officer=officer,
            award_type='Complimentary Letter'
        )
        AwardFactory(
            officer=officer,
            award_type='Honored Police Star'
        )
        AwardFactory(
            officer=officer,
            award_type='Lambert Tree'
        )
        OfficerHistoryFactory(
            officer=officer,
            unit__id=1001,
            unit__unit_name='001',
            unit__description='Hyde Park D',
            effective_date=date(2010, 1, 1),
            end_date=date(2011, 1, 1)
        )
        OfficerHistoryFactory(
            officer=officer,
            unit__id=1002,
            unit__unit_name='002',
            unit__description='Tactical',
            effective_date=date(2011, 1, 2),
            end_date=date(2012, 1, 1)
        )
        OfficerBadgeNumberFactory(
            officer=officer,
            star='123456',
            current=True
        )
        OfficerBadgeNumberFactory(
            officer=officer,
            star='123',
            current=False
        )
        OfficerBadgeNumberFactory(
            officer=officer,
            star='456',
            current=False
        )

        allegation = AllegationFactory()
        OfficerAllegationFactory(
            officer=officer,
            final_finding='SU',
            start_date=date(2000, 1, 1),
            allegation_category__category='Illegal Search',
            allegation=allegation,
            disciplined=True
        )
        ComplainantFactory(
            allegation=allegation,
            race='White',
            age=18,
            gender='M'
        )

        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]).to.eq({
            'id': 123,
            'full_name': 'Alex Mack',
            'unit': {
                'id': 1002,
                'unit_name': '002',
                'description': 'Tactical',
                'long_unit_name': 'Unit 002'
            },
            'rank': '5',
            'race': 'White',
            'badge': '123456',
            'historic_badges': ['123', '456'],
            'historic_units': [
                {
                    'id': 1002,
                    'unit_name': '002',
                    'description': 'Tactical',
                    'long_unit_name': 'Unit 002',
                }, {
                    'id': 1001,
                    'unit_name': '001',
                    'description': 'Hyde Park D',
                    'long_unit_name': 'Unit 001',
                }
            ],
            'gender': 'Male',
            'date_of_appt': '2017-02-27',
            'date_of_resignation': '2017-12-27',
            'active': 'Active',
            'birth_year': 1910,
            'complaint_records': {
                'count': 1,
                'sustained_count': 1,
                'items': [{'year': 2000, 'count': 1, 'sustained_count': 1}],
                'facets': [
                    {
                        'name': 'category',
                        'entries': [{'name': 'Illegal Search', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': 'Illegal Search', 'count': 1, 'sustained_count': 1}
                        ]}]
                    },
                    {
                        'name': 'complainant race',
                        'entries': [{'name': 'White', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': 'White', 'count': 1, 'sustained_count': 1}
                        ]}]
                    },
                    {
                        'name': 'complainant age',
                        'entries': [{'name': '<20', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': '<20', 'count': 1, 'sustained_count': 1}
                        ]}]
                    },
                    {
                        'name': 'complainant gender',
                        'entries': [{'name': 'Male', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': 'Male', 'count': 1, 'sustained_count': 1}
                        ]}]
                    }
                ]
            },
            'allegation_count': 1,
            'complaint_percentile': Decimal('99.8'),
            'honorable_mention_count': 1,
            'honorable_mention_percentile': 98,
            'has_visual_token': False,
            'sustained_count': 1,
            'discipline_count': 1,
            'civilian_compliment_count': 1,
            'trr_count': 1,
            'major_award_count': 2,
            'tags': ['Jason VanDyke'],
            'to': '/officer/123/alex-mack/',
            'url': 'http://test.com/officer/alex-mack/123',
            'current_salary': 9000,
            'unsustained_count': 0,
            'coaccusals': [],
            'current_allegation_percentile': None,
            'percentiles': []
        })

    def test_extract_info_complaint_record_null_category(self):
        officer = OfficerFactory()
        OfficerAllegationFactory(
            officer=officer,
            allegation_category=None,
            final_finding='SU',
            start_date=date(2000, 1, 2)
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation_category__category='Illegal Search',
            final_finding='NS',
            start_date=None
        )

        rows = self.extract_data()

        expect(rows).to.have.length(1)
        expect(rows[0]['complaint_records']['facets'][0]).to.eq({
            'name': 'category',
            'entries': [
                {'name': 'Unknown', 'count': 1, 'sustained_count': 1, 'items': [
                    {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 1}
                ]},
                {'name': 'Illegal Search', 'count': 1, 'sustained_count': 0, 'items': [
                    {'year': None, 'name': 'Illegal Search', 'count': 1, 'sustained_count': 0}
                ]}
            ]
        })

    def test_extract_info_complaint_record_null_complainant(self):
        officer = OfficerFactory()
        OfficerAllegationFactory(
            officer=officer,
            final_finding='UN',
            start_date=date(2000, 1, 2)
        )
        allegation = AllegationFactory()
        ComplainantFactory(
            allegation=allegation,
            race='White',
            gender='M',
            age=21)
        OfficerAllegationFactory(
            officer=officer,
            allegation=allegation,
            final_finding='UN',
            start_date=None
        )

        rows = self.extract_data()

        expect(rows).to.have.length(1)
        expect(rows[0]['complaint_records']['facets'][1:]).to.eq([
            {
                'name': 'complainant race',
                'entries': [
                    {'name': 'Unknown', 'count': 1, 'sustained_count': 0, 'items': [
                        {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 0}
                    ]},
                    {'name': 'White', 'count': 1, 'sustained_count': 0, 'items': [
                        {'year': None, 'name': 'White', 'count': 1, 'sustained_count': 0}
                    ]}
                ]
            },
            {
                'name': 'complainant age',
                'entries': [
                    {'name': 'Unknown', 'count': 1, 'sustained_count': 0, 'items': [
                        {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 0}
                    ]},
                    {'name': '20-30', 'count': 1, 'sustained_count': 0, 'items': [
                        {'year': None, 'name': '20-30', 'count': 1, 'sustained_count': 0}
                    ]}
                ]
            },
            {
                'name': 'complainant gender',
                'entries': [
                    {'name': 'Unknown', 'count': 1, 'sustained_count': 0, 'items': [
                        {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 0}
                    ]},
                    {'name': 'Male', 'count': 1, 'sustained_count': 0, 'items': [
                        {'year': None, 'name': 'Male', 'count': 1, 'sustained_count': 0}
                    ]}
                ]
            }
        ])

    def test_extract_info_complaint_record_complainant_empty_gender(self):
        allegation = AllegationFactory()
        ComplainantFactory(
            allegation=allegation,
            gender='')
        OfficerAllegationFactory(
            final_finding='UN',
            start_date=date(2000, 1, 2),
            allegation=allegation
        )

        rows = self.extract_data()

        expect(rows).to.have.length(1)
        expect(rows[0]['complaint_records']['facets'][3]).to.eq({
            'name': 'complainant gender',
            'entries': [{'name': 'Unknown', 'count': 1, 'sustained_count': 0, 'items': [
                {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 0}
            ]}]
        })

    def test_extract_info_complaint_record_complainant_unknown_race(self):
        allegation = AllegationFactory()
        ComplainantFactory(
            allegation=allegation,
            race='')
        OfficerAllegationFactory(
            final_finding='UN',
            start_date=date(2000, 1, 2),
            allegation=allegation
        )

        rows = self.extract_data()

        expect(rows).to.have.length(1)
        expect(rows[0]['complaint_records']['facets'][1]).to.eq({
            'name': 'complainant race',
            'entries': [{'name': 'Unknown', 'count': 1, 'sustained_count': 0, 'items': [
                {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 0}
            ]}]
        })

    def test_extract_info_complaint_record_complainant_null_age(self):
        allegation = AllegationFactory()
        ComplainantFactory(
            allegation=allegation,
            age=None)
        OfficerAllegationFactory(
            final_finding='UN',
            start_date=date(2000, 1, 2),
            allegation=allegation
        )

        rows = self.extract_data()

        expect(rows).to.have.length(1)
        expect(rows[0]['complaint_records']['facets'][2]).to.eq({
            'name': 'complainant age',
            'entries': [{'name': 'Unknown', 'count': 1, 'sustained_count': 0, 'items': [
                {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 0}
            ]}]
        })

    def test_extract_info_coaccusals(self):
        officer = OfficerFactory(id=1101)
        other_officer = OfficerFactory(id=1102)
        allegation1 = AllegationFactory()
        OfficerAllegationFactory(officer=officer, allegation=allegation1)
        OfficerAllegationFactory(officer=other_officer, allegation=allegation1)
        allegation2 = AllegationFactory()
        OfficerAllegationFactory(officer=officer, allegation=allegation2)
        OfficerAllegationFactory(officer=other_officer, allegation=allegation2)

        rows = self.extract_data()

        expect(rows).to.have.length(2)
        expect(rows[0]['coaccusals']).to.eq([
            {
                'id': 1102,
                'coaccusal_count': 2
            }
        ])
        expect(rows[1]['coaccusals']).to.eq([
            {
                'id': 1101,
                'coaccusal_count': 2
            }
        ])

    @override_settings(ALLEGATION_MIN='1988-01-01')
    @override_settings(ALLEGATION_MAX='2016-07-01')
    @override_settings(INTERNAL_CIVILIAN_ALLEGATION_MIN='2000-01-01')
    @override_settings(INTERNAL_CIVILIAN_ALLEGATION_MAX='2016-07-01')
    @override_settings(TRR_MIN='2004-01-08')
    @override_settings(TRR_MAX='2016-04-12')
    def test_extract_datum_percentiles(self):
        officer1 = OfficerFactory(id=1, appointed_date=date(2013, 1, 1))
        officer2 = OfficerFactory(id=2, appointed_date=date(2015, 3, 14))
        OfficerFactory(id=3, appointed_date=date(2014, 3, 1), resignation_date=date(2015, 4, 14))

        OfficerAllegationFactory(
            officer=officer1,
            allegation__incident_date=datetime(2015, 1, 1, tzinfo=pytz.utc),
            start_date=datetime(2015, 1, 1),
            allegation__is_officer_complaint=False)
        OfficerAllegationFactory(
            officer=officer1,
            start_date=date(2015, 1, 1),
            allegation__incident_date=datetime(2015, 1, 1, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False)
        OfficerAllegationFactory(
            officer=officer1,
            start_date=date(2016, 1, 22),
            allegation__incident_date=datetime(2016, 1, 1, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False)
        OfficerAllegationFactory.create_batch(
            2,
            officer=officer2,
            start_date=date(2017, 10, 19),
            allegation__incident_date=datetime(2016, 1, 16, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        OfficerAllegationFactory(
            officer=officer2,
            start_date=date(2017, 10, 19),
            allegation__incident_date=datetime(2016, 3, 15, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        OfficerAllegationFactory(
            officer=officer2,
            start_date=date(2017, 10, 19),
            allegation__incident_date=datetime(2017, 3, 15, tzinfo=pytz.utc),
            allegation__is_officer_complaint=True
        )
        TRRFactory(
            officer=officer1,
            trr_datetime=datetime(2017, 3, 15, tzinfo=pytz.utc),
        )
        TRRFactory(
            officer=officer1,
            trr_datetime=datetime(2016, 3, 15, tzinfo=pytz.utc),
        )
        rows = self.extract_data()

        expect(rows).to.have.length(3)
        expect(rows[0]['current_allegation_percentile']).to.eq('33.3333')
        expect(rows[0]['percentiles']).to.eq([
            {
                'id': 1,
                'year': 2014,
                'percentile_allegation': '0.0',
                'percentile_allegation_civilian': '0.0',
                'percentile_allegation_internal': '0.0',
                'percentile_trr': '0.0'
            },
            {
                'id': 1,
                'year': 2015,
                'percentile_allegation': '50.0',
                'percentile_allegation_civilian': '50.0',
                'percentile_allegation_internal': '0.0',
                'percentile_trr': '0.0'
            },
            {
                'id': 1,
                'year': 2016,
                'percentile_allegation': '33.3333',
                'percentile_allegation_civilian': '33.3333',
                'percentile_allegation_internal': '0.0',
                'percentile_trr': '66.6667'
            }
        ])
        expect(rows[1]['current_allegation_percentile']).to.eq('66.6667')
        expect(rows[1]['percentiles']).to.eq([
            {
                'id': 2,
                'year': 2016,
                'percentile_allegation': '66.6667',
                'percentile_allegation_civilian': '66.6667',
                'percentile_allegation_internal': '66.6667',
                'percentile_trr': '0.0'
            }
        ])
        expect(rows[2]['current_allegation_percentile']).to.eq('0.0')
        expect(rows[2]['percentiles']).to.eq([
            {
                'id': 3,
                'year': 2015,
                'percentile_allegation': '0.0',
                'percentile_allegation_civilian': '0.0',
                'percentile_allegation_internal': '0.0',
                'percentile_trr': '0.0'
            }
        ])

    @patch('officers.indexers.MIN_VISUAL_TOKEN_YEAR', 2016)
    @patch('officers.indexers.MAX_VISUAL_TOKEN_YEAR', 2016)
    @patch(
        'officers.indexers.officer_percentile.top_percentile',
        Mock(return_value=[{
            'id': 123,
            'year': 2016,
            'resignation_date': date(2017, 3, 4),
            'percentile_allegation': 23.4543,
            'percentile_allegation_civilian': 54.2342,
            'percentile_allegation_internal': 54.3432
        }])
    )
    def test_extract_datum_percentiles_missing_value(self):
        OfficerFactory(id=123)
        rows = self.extract_data()

        expect(rows).to.have.length(1)
        expect(rows[0]['percentiles']).to.eq([
            {
                'id': 123,
                'year': 2016,
                'percentile_allegation': '23.4543',
                'percentile_allegation_civilian': '54.2342',
                'percentile_allegation_internal': '54.3432'
            }
        ])


class JoinedNewTimelineEventIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        officer = Mock()
        with patch('officers.indexers.Officer.objects.filter', return_value=[officer]):
            expect(JoinedNewTimelineEventIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock(
            id=123,
            appointed_date=date(2012, 1, 1),
            get_unit_by_date=Mock(return_value=Mock(
                unit_name='001',
                description='Unit_001',
            )),
            get_rank_by_date=Mock(return_value='Police Officer'),
        )
        expect(JoinedNewTimelineEventIndexer().extract_datum(officer)).to.eq({
            'officer_id': 123,
            'date_sort': date(2012, 1, 1),
            'priority_sort': 10,
            'date': '2012-01-01',
            'kind': 'JOINED',
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
        })


class UnitChangeNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        officer_history = OfficerHistoryFactory(
            effective_date=date(2010, 1, 1),
            officer=OfficerFactory(appointed_date=date(2001, 2, 2))
        )
        OfficerHistoryFactory(
            effective_date=date(2010, 1, 1),
            officer=OfficerFactory(appointed_date=date(2010, 1, 1))
        )
        OfficerHistoryFactory(
            effective_date=None,
        )
        expect(list(UnitChangeNewTimelineEventIndexer().get_queryset())).to.eq([officer_history])

    def test_extract_datum(self):
        officer_history = Mock(
            officer_id=123,
            effective_date=date(2010, 3, 4),
            unit_name='003',
            unit_description='Unit_003',
            officer=Mock(get_rank_by_date=Mock(return_value='Police Officer'))
        )
        expect(UnitChangeNewTimelineEventIndexer().extract_datum(officer_history)).to.eq({
            'officer_id': 123,
            'date_sort': date(2010, 3, 4),
            'priority_sort': 20,
            'date': '2010-03-04',
            'kind': 'UNIT_CHANGE',
            'unit_name': '003',
            'unit_description': 'Unit_003',
            'rank': 'Police Officer',
        })


class CRNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        officer_allegation = Mock()

        with patch('officers.indexers.OfficerAllegation.objects.filter', return_value=[officer_allegation]):
            expect(CRNewTimelineEventIndexer().get_queryset()).to.eq([officer_allegation])

    def test_extract_datum(self):
        allegation = AllegationFactory(
            crid='123456',
            point=Point(35.5, 68.9),
        )
        AttachmentFileFactory(
            allegation=allegation,
            title='doc_2',
            url='url_2',
            preview_image_url='image_url_2',
            file_type=MEDIA_TYPE_DOCUMENT
        )
        AttachmentFileFactory(
            allegation=allegation,
            title='doc_1',
            url='url_1',
            preview_image_url='image_url_1',
            file_type=MEDIA_TYPE_DOCUMENT
        )
        officer = OfficerFactory(
            id=123,
            rank='Police Officer'
        )
        OfficerHistoryFactory(
            officer=officer,
            unit__unit_name='001',
            unit__description='Unit_001',
            effective_date=date(2011, 1, 1),
            end_date=date(2013, 1, 1))
        officer_allegation = OfficerAllegationFactory(
            allegation=allegation,
            officer=officer,
            start_date=date(2012, 1, 1),
            allegation_category=AllegationCategoryFactory(
                category='Illegal Search',
                allegation_name='Search of premise/vehicle without warrant',
            ),
            final_finding='UN',
            final_outcome='Unknown'
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)
        VictimFactory(allegation=allegation, gender='M', race='White', age=34)
        SalaryFactory(officer=officer, rank='Police Officer', spp_date=date(2012, 1, 1))

        expect(CRNewTimelineEventIndexer().extract_datum(officer_allegation)).to.eq({
            'officer_id': 123,
            'date_sort': date(2012, 1, 1),
            'priority_sort': 30,
            'date': '2012-01-01',
            'kind': 'CR',
            'crid': '123456',
            'category': 'Illegal Search',
            'subcategory': 'Search of premise/vehicle without warrant',
            'finding': 'Unfounded',
            'outcome': 'Unknown',
            'coaccused': 4,
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
            'victims': [
                {
                    'race': 'White',
                    'age': 34,
                    'gender': 'Male',
                }
            ],
            'point': {
                'lon': 35.5,
                'lat': 68.9
            },
            'attachments': [
                {
                    'title': 'doc_1',
                    'url': 'url_1',
                    'preview_image_url': 'image_url_1',
                    'file_type': 'document',
                },
                {
                    'title': 'doc_2',
                    'url': 'url_2',
                    'preview_image_url': 'image_url_2',
                    'file_type': 'document',
                },
            ]
        })


class CRNewTimelineEventPartialIndexerTestCase(TestCase):
    def test_get_queryset(self):
        allegation_123 = AllegationFactory(crid='123')
        allegation_456 = AllegationFactory(crid='456')
        officer_allegation_1 = OfficerAllegationFactory(allegation=allegation_123)
        officer_allegation_2 = OfficerAllegationFactory(allegation=allegation_123)
        OfficerAllegationFactory(allegation=allegation_456)

        indexer = CRNewTimelineEventPartialIndexer(updating_keys=['123'])
        expect(set(indexer.get_queryset())).to.eq({
            officer_allegation_1,
            officer_allegation_2,
        })

    def test_get_batch_queryset(self):
        allegation_123 = AllegationFactory(crid='123')
        allegation_456 = AllegationFactory(crid='456')
        officer_allegation_1 = OfficerAllegationFactory(allegation=allegation_123)
        officer_allegation_2 = OfficerAllegationFactory(allegation=allegation_123)
        OfficerAllegationFactory(allegation=allegation_456)

        expect(set(CRNewTimelineEventPartialIndexer().get_batch_queryset(keys=['123']))).to.eq({
            officer_allegation_1,
            officer_allegation_2,
        })

    def test_get_batch_update_docs_queries(self):
        OfficerNewTimelineEventDocType(meta={'id': '1'}, **{
            'crid': '123456',
            'kind': 'CR',
        }).save()

        OfficerNewTimelineEventDocType(meta={'id': '2'}, **{
            'crid': '789',
            'kind': 'CR',
        }).save()

        OfficerNewTimelineEventDocType(meta={'id': '3'}, **{
            'crid': '789123',
            'kind': 'CR',
        }).save()
        officers_index_alias.read_index.refresh()

        update_docs_queries = CRNewTimelineEventPartialIndexer().get_batch_update_docs_queries(
            keys=['123456', '789', '432']
        )

        expect(set(update_docs_query.crid for update_docs_query in update_docs_queries)).to.eq({
            '123456', '789',
        })


class AwardNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        AwardFactory(award_type='Honorable Mention')
        AwardFactory(award_type='Honorable Mention Ribbon Award')
        AwardFactory(award_type="Superintendent'S Honorable Mention")
        AwardFactory(award_type='Special Honorable Mention')
        AwardFactory(award_type='Complimentary Letter')
        AwardFactory(award_type='Department Commendation')
        award1 = AwardFactory(award_type='Life Saving Award')
        award2 = AwardFactory(award_type='Award Of Appreciation')
        award3 = AwardFactory(award_type='Problem Solving Award')
        expect(set([
            obj.pk for obj in AwardNewTimelineEventIndexer().get_queryset()
        ])).to.eq(set([award1.id, award2.id, award3.id]))

    def test_extract_datum(self):
        award = Mock(
            officer_id=123,
            start_date=date(2010, 3, 4),
            award_type='Honorable Mention',
            officer=Mock(
                get_rank_by_date=Mock(return_value='Police Officer'),
                get_unit_by_date=Mock(return_value=Mock(
                    unit_name='001',
                    description='Unit_001',
                )),
            ),
        )
        expect(AwardNewTimelineEventIndexer().extract_datum(award)).to.eq({
            'officer_id': 123,
            'date_sort': date(2010, 3, 4),
            'priority_sort': 40,
            'date': '2010-03-04',
            'kind': 'AWARD',
            'award_type': 'Honorable Mention',
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
        })


class TRRNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        trr = TRRFactory()
        TRRFactory(officer=None)

        expect([obj.id for obj in TRRNewTimelineEventIndexer().get_queryset()]).to.eq([trr.id])

    def test_extract_datum(self):
        trr = Mock(
            id=2,
            officer_id=123,
            trr_datetime=datetime(2010, 3, 4),
            firearm_used=False,
            taser=False,
            officer=Mock(
                get_rank_by_date=Mock(return_value='Police Officer'),
                get_unit_by_date=Mock(return_value=Mock(
                    unit_name='001',
                    description='Unit_001',
                )),
            ),
            point=Mock(
                x=34.5,
                y=67.8
            ),
        )

        expect(TRRNewTimelineEventIndexer().extract_datum(trr)).to.eq({
            'trr_id': 2,
            'officer_id': 123,
            'date_sort': date(2010, 3, 4),
            'priority_sort': 50,
            'date': '2010-03-04',
            'kind': 'FORCE',
            'taser': False,
            'firearm_used': False,
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
            'point': {
                'lat': 67.8,
                'lon': 34.5
            },
        })


class OfficerCoaccusalsIndexerTestCase(TestCase):
    def test_get_queryset(self):
        officer = OfficerFactory()
        expect(list(OfficerCoaccusalsIndexer().get_queryset())).to.eq([officer])

    def test_extract_datum(self):
        officer1 = OfficerFactory(appointed_date=date(2001, 1, 1))
        officer2 = OfficerFactory(
            first_name='Officer',
            last_name='456',
            race='White',
            gender='M',
            birth_year=1950,
            rank='Police Officer',
            appointed_date=date(2002, 1, 1),
            civilian_allegation_percentile=11.1111,
            internal_allegation_percentile=22.2222,
            trr_percentile=33.3333,
            complaint_percentile=44.4444,
        )
        officer3 = OfficerFactory(
            first_name='Officer',
            last_name='789',
            race='Black',
            gender='M',
            birth_year=1970,
            rank='Po As Detective',
            appointed_date=date(2003, 1, 1),
            civilian_allegation_percentile=55.5555,
            internal_allegation_percentile=66.6666,
            trr_percentile=77.7777,
            complaint_percentile=88.8888,
        )

        allegation1 = AllegationFactory(incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc))
        allegation2 = AllegationFactory(incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc))
        allegation3 = AllegationFactory(incident_date=datetime(2004, 1, 1, tzinfo=pytz.utc))
        allegation4 = AllegationFactory(incident_date=datetime(2005, 1, 1, tzinfo=pytz.utc))

        OfficerAllegationFactory(
            officer=officer2, allegation=allegation1, final_finding='SU', start_date=date(2003, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation2, final_finding='SU', start_date=date(2004, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation3, final_finding='NS', start_date=date(2005, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer1, allegation=allegation4, final_finding='NS', start_date=date(2006, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer2, allegation=allegation4, final_finding='NS', start_date=date(2006, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation4, final_finding='NS', start_date=date(2006, 1, 1)
        )

        expect(dict(OfficerCoaccusalsIndexer().extract_datum(officer1))).to.eq({
            'id': officer1.id,
            'coaccusals': [{
                'id': officer2.id,
                'full_name': 'Officer 456',
                'allegation_count': 2,
                'sustained_count': 1,
                'complaint_percentile': 44.4444,
                'race': 'White',
                'gender': 'Male',
                'birth_year': 1950,
                'coaccusal_count': 1,
                'rank': 'Police Officer',
                'percentile_allegation_civilian': '11.1111',
                'percentile_allegation_internal': '22.2222',
                'percentile_trr': '33.3333',
            }, {
                'id': officer3.id,
                'full_name': 'Officer 789',
                'allegation_count': 3,
                'sustained_count': 1,
                'complaint_percentile': 88.8888,
                'race': 'Black',
                'gender': 'Male',
                'birth_year': 1970,
                'coaccusal_count': 1,
                'rank': 'Po As Detective',
                'percentile_allegation_civilian': '55.5555',
                'percentile_allegation_internal': '66.6666',
                'percentile_trr': '77.7777',
            }]
        })


class RankChangeNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        salary1 = SalaryFactory(
            officer=officer1, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer1, salary=10000, year=2006, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        salary2 = SalaryFactory(
            officer=officer1, salary=15000, year=2007, rank='Sergeant', spp_date=date(2007, 1, 1),
            start_date=date(2005, 1, 1)
        )
        salary3 = SalaryFactory(
            officer=officer2, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        salary4 = SalaryFactory(
            officer=officer2, salary=15000, year=2006, rank='Detective', spp_date=date(2006, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer2, salary=20000, year=2007, rank='Detective', spp_date=date(2006, 1, 1),
            start_date=date(2005, 1, 1)
        )
        expect(RankChangeNewTimelineEventIndexer().get_queryset()).to.eq([salary1, salary2, salary3, salary4])

    def test_extract_datum(self):
        salary = Mock(
            officer_id=123,
            spp_date=date(2005, 1, 1),
            salary=10000,
            year=2015,
            rank='Police Officer',
            start_date=date(2010, 3, 4),
            officer=Mock(
                get_unit_by_date=Mock(return_value=Mock(
                    unit_name='001',
                    description='Unit_001',
                )),
            ),
        )
        expect(RankChangeNewTimelineEventIndexer().extract_datum(salary)).to.eq({
            'officer_id': 123,
            'date_sort': date(2005, 1, 1),
            'priority_sort': 25,
            'date': '2005-01-01',
            'kind': 'RANK_CHANGE',
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
        })
