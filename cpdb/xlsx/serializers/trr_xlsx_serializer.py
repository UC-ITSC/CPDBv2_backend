import pytz

from rest_framework.serializers import Serializer, CharField, IntegerField, DateTimeField, NullBooleanField


class TRRXlsxSerializer(Serializer):
    id = IntegerField()
    beat = IntegerField(allow_null=True)
    block = CharField(allow_null=True)
    direction = CharField(allow_null=True)
    street = CharField(allow_null=True)
    location = CharField(allow_null=True)
    trr_datetime = DateTimeField(format='%Y-%m-%d', allow_null=True, default_timezone=pytz.utc)
    indoor_or_outdoor = CharField(allow_null=True)
    lighting_condition = CharField(allow_null=True)
    weather_condition = CharField(allow_null=True)
    notify_OEMC = NullBooleanField()
    notify_district_sergeant = NullBooleanField()
    notify_OP_command = NullBooleanField()
    notify_DET_division = NullBooleanField()
    number_of_weapons_discharged = IntegerField(allow_null=True)
    party_fired_first = CharField(allow_null=True)
    location_recode = CharField(allow_null=True)
    taser = NullBooleanField()
    total_number_of_shots = IntegerField(allow_null=True)
    firearm_used = NullBooleanField()
    number_of_officers_using_firearm = IntegerField(allow_null=True)
    officer_assigned_beat = CharField(allow_null=True)
    officer_unit = CharField(allow_null=True, source='officer_unit.unit_name')
    officer_unit_detail = CharField(allow_null=True, source='officer_unit_detail.unit_name')
    officer_on_duty = NullBooleanField()
    officer_in_uniform = NullBooleanField()
    officer_injured = NullBooleanField()
    officer_rank = CharField(allow_null=True)
    subject_id = IntegerField(allow_null=True)
    subject_armed = NullBooleanField()
    subject_injured = NullBooleanField()
    subject_alleged_injury = NullBooleanField()
    subject_age = IntegerField(allow_null=True)
    subject_birth_year = IntegerField(allow_null=True)
    subject_gender = CharField(allow_null=True)
    subject_race = CharField(allow_null=True)
