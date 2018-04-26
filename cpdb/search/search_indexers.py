from tqdm import tqdm
import csv

from cms.models import FAQPage, ReportPage
from data.models import Officer, PoliceUnit, Area, OfficerHistory, Allegation
from search.doc_types import (
    FAQDocType, ReportDocType, OfficerDocType,
    UnitDocType, AreaDocType,
    UnitOfficerDocType, CrDocType
)
from search.indices import autocompletes_alias
from search.serializers import RacePopulationSerializer
from django.conf import settings


def extract_text_from_value(value):
    return '\n'.join([block['text'] for block in value['blocks']])


class BaseIndexer(object):
    doc_type_klass = None

    def __init__(self, index_name=None):
        self.index_name = index_name or autocompletes_alias.new_index_name

    def get_queryset(self):
        raise NotImplementedError

    def extract_datum(self, datum):
        raise NotImplementedError

    def extract_datum_with_id(self, datum):
        '''
        Ensure that the indexed document has the same ID as its corresponding database record.
        We can't do this to indexer classes where extract_datum() returns a list because
        multiple documents cannot share the same ID.
        '''
        extracted_data = self.extract_datum(datum)
        if not isinstance(extracted_data, list):
            extracted_data['meta'] = {'id': datum.pk}
        return extracted_data

    def save_doc(self, extracted_data, index=None):
        extracted_data['_index'] = self.index_name
        doc = self.doc_type_klass(**extracted_data)
        doc.save()

    def index_datum(self, datum):
        extracted_data = self.extract_datum_with_id(datum)
        if isinstance(extracted_data, list):
            [self.save_doc(entry) for entry in extracted_data]
        else:
            self.save_doc(extracted_data)

    def index_data(self):
        for datum in tqdm(
            self.get_queryset(),
            desc='Indexing {doc_type_name}'.format(
                doc_type_name=self.doc_type_klass._doc_type.name)):
            self.index_datum(datum)


class FAQIndexer(BaseIndexer):
    doc_type_klass = FAQDocType

    def get_queryset(self):
        return FAQPage.objects.all()

    def extract_datum(self, datum):
        fields = datum.fields

        return {
            'question': extract_text_from_value(fields['question_value']),
            'answer': extract_text_from_value(fields['answer_value']),
            'tags': datum.tags
        }


class ReportIndexer(BaseIndexer):
    doc_type_klass = ReportDocType

    def get_queryset(self):
        return ReportPage.objects.all()

    def extract_datum(self, datum):
        fields = datum.fields

        return {
            'publication': fields['publication_value'],
            'author': fields['author_value'],
            'excerpt': extract_text_from_value(fields['excerpt_value']),
            'title': extract_text_from_value(fields['title_value']),
            'publish_date': fields['publish_date_value'],
            'tags': datum.tags
        }


class OfficerIndexer(BaseIndexer):
    doc_type_klass = OfficerDocType

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, datum):
        return {
            'allegation_count': datum.allegation_count,
            'full_name': datum.full_name,
            'badge': datum.current_badge,
            'to': datum.v2_to,
            'visual_token_background_color': datum.visual_token_background_color,
            'tags': datum.tags,
            'sustained_count': datum.sustained_count,
            'birth_year': datum.birth_year,
            'unit': datum.last_unit,
            'rank': datum.rank,
            'race': datum.race,
            'sex': datum.gender_display
        }


class UnitIndexer(BaseIndexer):
    doc_type_klass = UnitDocType

    def get_queryset(self):
        return PoliceUnit.objects.all()

    def extract_datum(self, datum):
        return {
            'name': datum.unit_name,
            'description': datum.description,
            'url': datum.v1_url,
            'to': datum.v2_to,
            'active_member_count': datum.active_member_count,
            'member_count': datum.member_count
        }


class UnitOfficerIndexer(BaseIndexer):
    doc_type_klass = UnitOfficerDocType

    def get_queryset(self):
        return OfficerHistory.objects.all()

    def extract_datum(self, datum):
        return {
            'full_name': datum.officer.full_name,
            'badge': datum.officer.current_badge,
            'to': datum.officer.v2_to,
            'allegation_count': datum.officer.allegation_count,
            'visual_token_background_color': datum.officer.visual_token_background_color,
            'unit_name': datum.unit.unit_name,
            'unit_description': datum.unit.description,
            'sustained_count': datum.officer.sustained_count,
            'birth_year': datum.officer.birth_year,
            'unit': datum.officer.last_unit,
            'rank': datum.officer.rank,
            'race': datum.officer.race,
            'sex': datum.officer.gender_display
        }


class AreaIndexer(BaseIndexer):
    doc_type_klass = AreaDocType
    alderman_list = {}

    def get_queryset(self):
        if not self.alderman_list:
            self.alderman_list = AreaIndexer.get_alderman_list_from_file()
        return Area.objects.all()

    @staticmethod
    def get_alderman_list_from_file():
        file_name = str(settings.APPS_DIR.path('search/csv_data/aldermen.csv'))
        with open(file_name, 'rb') as csv_file:
            rows = csv.reader(csv_file)
            aldermen = {row[0].strip(): row[1].strip() for row in rows}
        return aldermen

    def _get_area_tag(self, area_type):
        return Area.SESSION_BUILDER_MAPPING.get(area_type, area_type).replace('_', ' ')

    def extract_datum(self, datum):
        tags = list(datum.tags)
        area_tag = self._get_area_tag(datum.area_type)
        if area_tag and area_tag not in tags:
            tags.append(area_tag)
        alderman = self.alderman_list.get(datum.name) if datum.area_type == 'ward' else ''

        return {
            'name': datum.name,
            'area_type': area_tag.replace(' ', '-'),
            'url': datum.v1_url,
            'tags': tags,
            'allegation_count': datum.allegation_count,
            'officers_most_complaint': list(datum.get_officers_most_complaints()),
            'most_common_complaint': list(datum.get_most_common_complaint()),
            'race_count': RacePopulationSerializer(
                datum.racepopulation_set.order_by('-count'),
                many=True).data,
            'median_income': datum.median_income,
            'alderman': alderman,
        }


class IndexerManager(object):
    def __init__(self, indexers=None):
        self.indexers = indexers or []

    def _build_mapping(self):
        autocompletes_alias.write_index.close()
        for indexer in self.indexers:
            indexer.doc_type_klass.init(index=autocompletes_alias.new_index_name)
        autocompletes_alias.write_index.open()

    def _index_data(self):
        for indexer_klass in self.indexers:
            a = indexer_klass()
            a.index_data()

    def rebuild_index(self, migrate_doc_types=[]):
        with autocompletes_alias.indexing():
            self._build_mapping()
            autocompletes_alias.migrate(migrate_doc_types)
            self._index_data()


class CrIndexer(BaseIndexer):
    doc_type_klass = CrDocType

    def get_queryset(self):
        return Allegation.objects.all()

    def extract_datum(self, datum):
        return {
            'crid': datum.crid,
            'to': datum.v2_to
        }
