import datetime
import json
import os

import pandas as pd
from django.core.management.base import BaseCommand

from maps.models import Point


def read_metadata(metadata_path):
    with open(metadata_path, encoding="utf-8") as f:
        data = json.load(f, encoding='utf-8')
    return data


def read_dataset(dataset_path):
    flooded_df = pd.read_csv(dataset_path, names=['filename', 'font', 'class', 'height'])

    flooded_df['year'], flooded_df['month'], flooded_df['day'] = None, None, None
    flooded_df['latitude'], flooded_df['longitude'] = None, None

    return flooded_df


def handle_eu_floods_metadata(entry, metadata):
    image_entry = [obj for obj in metadata if str(obj['pageid']) == str(entry['filename'])][0]

    date_taken = image_entry['capture_time']
    date_taken = datetime.datetime.strptime(date_taken, '%Y-%m-%dT%H:%M:%S').timetuple()

    entry['longitude'] = image_entry['coordinates']['lon']
    entry['latitude'] = image_entry['coordinates']['lat']

    entry['year'] = date_taken.tm_year
    entry['month'] = date_taken.tm_mon
    entry['day'] = date_taken.tm_mday

    return entry


def handle_mediaeval_metadata(entry, metadata):
    image_entry = [obj for obj in metadata['images'] if obj['image_id'] == str(entry['filename'])][0]

    date_taken = image_entry['date_taken'].split(".")[0]
    date_taken = datetime.datetime.strptime(date_taken, '%Y-%m-%d %H:%M:%S').timetuple()

    entry['year'] = date_taken.tm_year
    entry['month'] = date_taken.tm_mon
    entry['day'] = date_taken.tm_mday

    entry['longitude'] = image_entry['longitude']
    entry['latitude'] = image_entry['latitude']

    return entry


def get_flooded_info(flooded_info, mediaeval_train, mediaeval_test, european_floods):
    for index, row in flooded_info.iterrows():

        if row['font'] == "european_floods_2013":
            handle_eu_floods_metadata(row, european_floods)
        elif row['font'] == "mediaeval_2017_train":
            handle_mediaeval_metadata(row, mediaeval_train)
        elif row['font'] == "mediaeval_2017_test":
            handle_mediaeval_metadata(row, mediaeval_test)
        else:
            raise ValueError("Font not recognized.")

        flooded_info.iloc[index] = row

    return flooded_info


def add_to_db(df):
    for index, row in df.iterrows():

        if row['font'] == "mediaeval_2017_test":
            source = "MediaEval 2017 Test"
        elif row['font'] == "mediaeval_2017_train":
            source = "MediaEval 2017 Train"
        elif row['font'] == "european_floods_2013":
            source = "European Floods 2013 "
        else:
            raise ValueError("Font not recognized.")

        query = Point.objects.create(source=source,
                                     name=row['filename'],
                                     longitude=row['longitude'],
                                     latitude=row['latitude'],
                                     label=int(row['class']),
                                     flood_height=round(row['height'], 4),
                                     date="{}-{}-{}".format(row['year'], row['month'], row['day']),
                                     image="images/{}.jpg".format(row['filename']))
        query.save()


def delete_not_used_files(result):
    names = [str(name) + ".jpg" for name in result['filename'].tolist()]
    to_delete = [file for file in os.listdir('./media/images/') if file not in names]
    for file in to_delete:
        os.remove("./media/images/" + file)


class Command(BaseCommand):
    help = 'Seeds the database.'

    def handle(self, *args, **options):
        Point.objects.all().delete()
        current_path = os.path.dirname(os.path.abspath(__file__))

        mediaeval_test_mdt = read_metadata("{}/files_init_db/mediaeval2017_testset_metadata.json".format(current_path))
        mediaeval_train_mdt = read_metadata("{}/files_init_db/mediaeval2017_devset_metadata.json".format(current_path))
        european_floods_mdt = read_metadata("{}/files_init_db/european_floods_2013_metadata.json".format(current_path))
        flood_heights = read_dataset("{}/files_init_db/flood_height.csv".format(current_path))
        result = get_flooded_info(flood_heights, mediaeval_train_mdt, mediaeval_test_mdt, european_floods_mdt)

        delete_not_used_files(result)
        add_to_db(result)
