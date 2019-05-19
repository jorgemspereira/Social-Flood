import datetime
import json
import os

import pandas as pd
from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand

from maps.models import Point


def read_dataset_and_metadata(dataset_path, metadata_path):
    all_df = pd.read_csv(dataset_path, names=['filename', 'class'])
    flooded_df = all_df.drop(all_df[all_df['class'] != 1].index).reset_index(drop=True)
    flooded_df = flooded_df.drop(['class'], axis=1).reset_index(drop=True)

    flooded_df['year'], flooded_df['month'], flooded_df['day'] = None, None, None
    flooded_df['latitude'], flooded_df['longitude'] = None, None

    with open(metadata_path, encoding="utf-8") as f:
        data = json.load(f, encoding='utf-8')

    return flooded_df, data


def get_flooded_mediaeval_info(classification_path, metadata_path):
    flooded_df, metadata = read_dataset_and_metadata(classification_path, metadata_path)

    for index, row in flooded_df.iterrows():
        try:
            image_entry = [obj for obj in metadata['images'] if obj['image_id'] == str(row['filename'])][0]

            date_taken = image_entry['date_taken'].split(".")[0]
            date_taken = datetime.datetime.strptime(date_taken, '%Y-%m-%d %H:%M:%S').timetuple()

            row['year'] = date_taken.tm_year
            row['month'] = date_taken.tm_mon
            row['day'] = date_taken.tm_mday

            row['longitude'] = image_entry['longitude']
            row['latitude'] = image_entry['latitude']

            flooded_df.iloc[index] = row
        except TypeError:
            pass

    return flooded_df.dropna().reset_index(drop=True)


def get_flooded_europeanfloods_info(classification_path, metadata_path):
    flooded_df, metadata = read_dataset_and_metadata(classification_path, metadata_path)

    for index, row in flooded_df.iterrows():
        try:
            image_entry = [obj for obj in metadata if str(obj['pageid']) == str(row['filename'])][0]

            date_taken = image_entry['capture_time']
            date_taken = datetime.datetime.strptime(date_taken, '%Y-%m-%dT%H:%M:%S').timetuple()

            row['year'] = date_taken.tm_year
            row['month'] = date_taken.tm_mon
            row['day'] = date_taken.tm_mday

            row['longitude'] = image_entry['coordinates']['lon']
            row['latitude'] = image_entry['coordinates']['lat']

            flooded_df.iloc[index] = row
        except (KeyError, IndexError, TypeError):
            pass

    return flooded_df.dropna().reset_index(drop=True)


def add_to_db(df, source):
    for index, row in df.iterrows():
        query = Point.objects.create(source=source,
                                     name=row['filename'],
                                     longitude=row['longitude'],
                                     latitude=row['latitude'],
                                     date="{}-{}-{}".format(row['year'], row['month'], row['day']),
                                     image="images/{}.jpg".format(row['filename']))
        query.save()


class Command(BaseCommand):
    help = 'Seeds the database.'

    def handle(self, *args, **options):
        Point.objects.all().delete()

        current_path = os.path.dirname(os.path.abspath(__file__))

        mediaeval_test_df = get_flooded_mediaeval_info(
            "{}/files_init_db/mediaeval2017_testset_gt.csv".format(current_path),
            "{}/files_init_db/mediaeval2017_testset_metadata.json".format(current_path))

        mediaeval_train_df = get_flooded_mediaeval_info(
            "{}/files_init_db/mediaeval2017_devset_gt.csv".format(current_path),
            "{}/files_init_db/mediaeval2017_devset_metadata.json".format(current_path))

        european_floods_df = get_flooded_europeanfloods_info(
            "{}/files_init_db/european_floods_2013_gt.csv".format(current_path),
            "{}/files_init_db/european_floods_2013_metadata.json".format(current_path))

        add_to_db(mediaeval_test_df, "MediaEval 2017 Test Split")
        add_to_db(mediaeval_train_df, "MediaEval 2017 Train Split")
        add_to_db(european_floods_df, "European Floods 2013")
