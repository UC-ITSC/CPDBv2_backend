import json
import gzip
from tempfile import NamedTemporaryFile

from django.core.management import BaseCommand
from django.conf import settings
from django.db import connection
from django.contrib.gis.geos.factory import fromstr

from azure.storage.blob import BlockBlobService, PublicAccess, ContentSettings
from azure.storage.common.models import CorsRule


# pragma: no cover
class Command(BaseCommand):
    help = (
        'Upload heatmap geojsons to Azure storage.'
        'Rerun whenever we import new data.'
        )

    _prev_total = 0

    def get_heatmap_cluster_data(self):
        kursor = connection.cursor()

        grid_size = 0.0005

        kursor.execute('''
            SELECT
                COUNT( point ) AS count,
                ST_AsText( ST_Centroid(ST_Collect( point )) ) AS center
            FROM data_allegation WHERE point IS NOT NULL
            GROUP BY
                ST_SnapToGrid( ST_SetSRID(point, 4326), %s, %s)
            ''' % (grid_size, grid_size)
            )
        kclusters = kursor.fetchall()
        ret = {'features': [], 'type': 'FeatureCollection'}

        for cluster in kclusters:
            point = fromstr(cluster[1])
            weight = cluster[0]

            allegation_json = {
                "type": "Feature",
                "properties": {
                    "weight": weight
                },
                'geometry': {
                    'coordinates': [point.x, point.y],
                    'type': 'Point'
                }
            }
            ret['features'].append(allegation_json)

        return json.dumps(ret)

    def save_to_gzip_file(self, content):
        tmp_file = NamedTemporaryFile(delete=False)
        with gzip.open(tmp_file.name, 'wb') as f:
            f.write(content)
        return tmp_file.name

    def handle(self, *args, **options):
        block_blob_service = BlockBlobService(
            account_name=settings.AZURE_STORAGE_ACCOUNT_NAME, account_key=settings.AZURE_STORAGE_ACCOUNT_KEY)
        block_blob_service.create_container('heatmap', public_access=PublicAccess.Blob)
        block_blob_service.set_blob_service_properties(cors=[CorsRule(['*'], ['GET'])])
        block_blob_service.create_blob_from_path(
            'heatmap',
            'cluster.geojson',
            file_path=self.save_to_gzip_file(self.get_heatmap_cluster_data()),
            content_settings=ContentSettings(content_type='application/json', content_encoding='gzip')
        )
