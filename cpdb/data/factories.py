import random

from django.contrib.gis.geos import MultiPolygon, Polygon, MultiLineString, LineString
from django.contrib.contenttypes.models import ContentType

import factory
from faker import Faker
from wagtail.wagtailcore.models import Page

from data.models import Area, Investigator, LineArea, Officer
from data.constants import RANKS, ACTIVE_CHOICES

fake = Faker()


class AreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Area

    name = factory.LazyFunction(lambda: fake.word())
    area_type = 'school-grounds'
    polygon = factory.LazyFunction(lambda: MultiPolygon(Polygon((
        (87.940101, 42.023135),
        (87.523661, 42.023135),
        (87.523661, 41.644286),
        (87.940101, 41.644286),
        (87.940101, 42.023135)))))


class LineAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LineArea

    name = factory.LazyFunction(lambda: fake.word())
    linearea_type = 'passageway'
    geom = factory.LazyFunction(lambda: MultiLineString(
        LineString(
            (-87.6543545842184386, 41.7741537537218477),
            (-87.6543453548284504, 41.7738192794681069)
        )
    ))


class InvestigatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Investigator
        django_get_or_create = ('name',)

    name = factory.LazyFunction(lambda: fake.name())
    raw_name = factory.LazyAttribute(lambda o: o.name.upper())
    current_rank = factory.LazyFunction(lambda: fake.word())


class RootPageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Page

    title = 'Root'
    slug = 'root'
    content_type = ContentType.objects.get_for_model(Page)


class OfficerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Officer

    full_name = factory.LazyFunction(lambda: fake.name())
    gender = factory.LazyFunction(lambda: random.choice(['M', 'F']))
    race = 'White'
    appointed_date = factory.LazyFunction(lambda: fake.date_time().date())
    rank = factory.LazyFunction(lambda: random.choice(RANKS)[0])
    birth_year = factory.LazyFunction(fake.year)
    active = factory.LazyFunction(lambda: random.choice(ACTIVE_CHOICES)[0])
