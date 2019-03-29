from rest_framework import serializers

from data.models import Allegation
from pinboard.serializers.officer_card_serializer import OfficerCardSerializer


class AllegationSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    officers = serializers.SerializerMethodField()

    def get_officers(self, obj):
        officers = [officer_allegation.officer for officer_allegation in obj.prefetch_officer_allegations]
        return OfficerCardSerializer(officers, many=True).data

    def get_category(self, obj):
        try:
            return obj.most_common_category.category
        except AttributeError:
            return 'Unknown'

    class Meta:
        model = Allegation
        fields = (
            'crid',
            'incident_date',
            'v2_to',
            'category',
            'officers',
        )


class AllegationCardSerializer(AllegationSerializer):
    point = serializers.SerializerMethodField()

    def get_point(self, obj):
        if obj.point is not None:
            return {'lon': obj.point.x, 'lat': obj.point.y}
        else:
            return None

    class Meta(AllegationSerializer.Meta):
        fields = AllegationSerializer.Meta.fields + ('point',)
