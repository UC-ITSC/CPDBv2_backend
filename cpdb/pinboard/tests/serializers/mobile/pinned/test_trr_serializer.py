from datetime import datetime

from django.test import TestCase
from django.contrib.gis.geos import Point

import pytz
from robber import expect

from trr.factories import TRRFactory, ActionResponseFactory
from pinboard.serializers.mobile.pinned import PinnedTRRMobileSerializer


class PinnedTRRMobileSerializerTestCase(TestCase):
    def test_serialization(self):
        trr = TRRFactory(
            id=1,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(-32.5, 61.3),
        )
        ActionResponseFactory(trr=trr, force_type='Physical Force - Stunning', action_sub_category='4')
        serializer = PinnedTRRMobileSerializer(trr)
        expect(serializer.data).to.eq({
            'id': 1,
            'trr_datetime': '2004-01-01',
            'category': 'Physical Force - Stunning',
            'point': {'lon': -32.5, 'lat': 61.3}
        })
