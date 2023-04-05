'''
Eagle class
'''

import datetime
from pathlib import Path
import json
import concurrent.futures
import requests
from loguru import logger


class Eagle:
    def __init__(self, domain='http://localhost', port=41595):
        self.domain = domain
        self.port = port
        self.host = f'{domain}:{port}'

    def get_img_info_from_lib_path(self, source_path: str, name_start_filters=[], max_workers=4) -> list:
        '''
        Get all images INFO (meta) from path of source library

        For example, there is a path of library is `/path/to/your/test.library`

        '''
        imgs_info = []

        def load_id(meta_path):
            data = {}
            with open(meta_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.loads(f.read())
                    name = data.get('name')
                    for name_start_filter in name_start_filters:
                        if not name.startswith(name_start_filter):
                            return {}
                except Exception as e:
                    logger.warning(f'[Eagle] {e}')
            return data

        logger.debug('[Eagle] Start getting images INFO...')
        st = datetime.datetime.now()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            get_id_job = {
                executor.submit(load_id, meta_path): meta_path for meta_path in Path(source_path).glob('**/metadata.json')
            }
            for future in concurrent.futures.as_completed(get_id_job):
                try:
                    data = future.result()
                    if data is not None:
                        imgs_info.append(data)
                except Exception as e:
                    logger.error(e)
        ed = datetime.datetime.now()
        logger.debug(f'[Eagle] Get all images INFO cost :: {(ed - st).total_seconds():.2f} sec(s)')

        return imgs_info

    def add_from_url(self, url: str, name: str, tags=None, website='', annotation='') -> dict:
        '''
        Add a new image or materials from the given url
        '''
        if tags is None:
            tags = []
        data = {
            'url': url,
            'name': name,
            'website': website,
            'tags': tags,
            'annotation': annotation
        }
        resp = requests.post(f'{self.host}/api/item/addFromURL', json=data)
        return resp.json()

    def get_img_list_info(self, max_image_number: int, name_start_filter='') -> list:
        '''
        Get all images information in a list
        '''
        resp = requests.get(f'{self.host}/api/item/list?limit={max_image_number}')
        data = resp.json().get('data')
        if name_start_filter != '':
            data = [d for d in data if d.get('name').startswith(name_start_filter)]
        return data

    def set_tag_with_id(self, image_id: int, tags: list):
        '''
        Set tags to an image with its ID
        '''
        data = {
            'id': image_id,
            'tags': tags
        }
        resp = requests.post(f'{self.host}/api/item/update', json=data)
        return resp.json()
