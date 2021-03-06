from rest_framework import serializers
from django.db.models import Prefetch, Exists, OuterRef

import pytz

from data.models import Investigator
from shared.serializer import NoNullSerializer, OfficerPercentileSerializer


class ComplainantMobileSerializer(NoNullSerializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class VictimMobileSerializer(NoNullSerializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class AttachmentFileMobileSerializer(NoNullSerializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()
    file_type = serializers.CharField()
    id = serializers.CharField()


class AllegationCategoryMobileSerializer(NoNullSerializer):
    category = serializers.CharField()
    allegation_name = serializers.CharField()


class CoaccusedMobileSerializer(NoNullSerializer):
    id = serializers.IntegerField(source='officer.id')
    full_name = serializers.CharField(source='officer.full_name')
    rank = serializers.CharField(source='officer.rank')
    allegation_count = serializers.IntegerField(source='officer.allegation_count')
    final_outcome = serializers.CharField()
    final_finding = serializers.CharField(source='final_finding_display')
    category = serializers.CharField()

    percentile_allegation = serializers.DecimalField(
        source='officer.complaint_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )
    percentile_allegation_civilian = serializers.DecimalField(
        source='officer.civilian_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )
    percentile_allegation_internal = serializers.DecimalField(
        source='officer.internal_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )
    percentile_trr = serializers.DecimalField(
        source='officer.trr_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )


class InvestigatorMobileSerializer(NoNullSerializer):
    officer_id = serializers.IntegerField(required=False, source='investigator.officer.id')
    involved_type = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()

    percentile_allegation = serializers.DecimalField(
        required=False, source='investigator.officer.complaint_percentile', max_digits=6, decimal_places=4)
    percentile_allegation_civilian = serializers.DecimalField(
        required=False, source='investigator.officer.civilian_allegation_percentile', max_digits=6, decimal_places=4)
    percentile_allegation_internal = serializers.DecimalField(
        required=False, source='investigator.officer.internal_allegation_percentile', max_digits=6, decimal_places=4)
    percentile_trr = serializers.DecimalField(
        required=False, source='investigator.officer.trr_percentile', max_digits=6, decimal_places=4)

    def get_involved_type(self, obj):
        return 'investigator'

    def get_full_name(self, obj):
        return getattr(obj.investigator.officer, 'full_name', obj.investigator.full_name)

    def get_badge(self, obj):
        incident_date = obj.allegation.incident_date
        pre_2006 = incident_date and incident_date.year < 2006
        if pre_2006 or obj.current_star or obj.has_badge_number:
            return 'CPD'
        else:
            return 'COPA/IPRA'


class PoliceWitnessMobileSerializer(OfficerPercentileSerializer):
    officer_id = serializers.IntegerField(source='id')
    involved_type = serializers.SerializerMethodField()
    full_name = serializers.CharField()
    allegation_count = serializers.IntegerField()
    sustained_count = serializers.IntegerField()

    def get_involved_type(self, obj):
        return 'police_witness'


class CRMobileSerializer(NoNullSerializer):
    crid = serializers.CharField()
    most_common_category = AllegationCategoryMobileSerializer()
    coaccused = serializers.SerializerMethodField()
    complainants = ComplainantMobileSerializer(many=True)
    victims = VictimMobileSerializer(many=True)
    summary = serializers.CharField()
    point = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    start_date = serializers.DateField(source='first_start_date', format='%Y-%m-%d')
    end_date = serializers.DateField(source='first_end_date', format='%Y-%m-%d')
    address = serializers.CharField()
    location = serializers.CharField()
    beat = serializers.SerializerMethodField()
    involvements = serializers.SerializerMethodField()

    attachments = AttachmentFileMobileSerializer(source='filtered_attachment_files', many=True)

    def get_coaccused(self, obj):
        officer_allegations = obj.officer_allegations.select_related(
            'allegation_category'
        ).prefetch_related('officer')

        return CoaccusedMobileSerializer(officer_allegations, many=True).data

    def get_point(self, obj):
        if obj.point is not None:
            return {'lon': obj.point.x, 'lat': obj.point.y}
        else:
            return None

    def get_involvements(self, obj):
        return (
            InvestigatorMobileSerializer(self.get_investigator_allegation(obj), many=True).data +
            PoliceWitnessMobileSerializer(obj.police_witnesses.all(), many=True).data
        )

    def get_investigator_allegation(self, obj):
        return obj.investigatorallegation_set \
            .prefetch_related(Prefetch('investigator__officer')) \
            .annotate(
                has_badge_number=Exists(
                    Investigator.objects.filter(
                        id=OuterRef('investigator_id'),
                        officer__officerbadgenumber__isnull=False
                    )
                )
            )

    def get_beat(self, obj):
        return obj.beat.name if obj.beat is not None else None
