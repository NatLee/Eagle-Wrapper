import datetime
from pathlib import Path
import json
import concurrent.futures

import requests
from loguru import logger

EAGLE_DOMAIN = 'http://localhost'
EAGLE_PORT = 41595
EAGLE_HOST = f'{EAGLE_DOMAIN}:{EAGLE_PORT}'


def get_image_id_with_path(source_path:str, name_start_filters=[], max_workers=10) -> list:
    images_info = []

    def load_id(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            image_id = data.get('id')
            name = data.get('name')
            tags = data.get('tags')
            if image_id is not None and name is not None and tags is not None:
                if name_start_filters != []:
                    for name_start_filter in name_start_filters:
                        if name.startswith(name_start_filter):
                            return image_id, name, tags
                else:
                    return image_id, name, tags
        return None

    logger.debug('[Eagle][get_image_id_with_path] Start getting image IDs...')
    st = datetime.datetime.now()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        get_id_job = {executor.submit(load_id, meta_path): meta_path for meta_path in Path(source_path).glob('**/metadata.json')}
        for future in concurrent.futures.as_completed(get_id_job):
            #logger.info(get_id_job[future])
            try:
                data = future.result()
                if data is not None:
                    images_info.append(data)
            except Execption as e:
                logger.error(e)
    ed = datetime.datetime.now()
    logger.debug(f'[Eagle][get_image_id_with_path] Cost :: {ed-st}')

    return images_info


def add_from_url(url:str, name:str, tags=[], website='', annotation='', host=EAGLE_HOST):
    data = {
        'url': url,
        'name': name,
        'website': website,
        'tags': tags,
        'annotation': annotation
    }
    requests.post(f'{host}/api/item/addFromURL', json=data)
    return


def get_image_list_info(max_image_number:int, name_start_filter=None, host=EAGLE_HOST) -> list:
    req = requests.get(f'{host}/api/item/list?limit={max_image_number}')
    data = req.json().get('data')
    if name_start_filter is not None:
        data = [d for d in data if d.get('name').startswith(name_start_filter)] 
    return data


def set_tag_with_id(image_id:int, tags:list, host=EAGLE_HOST):
    data = {
            'id': image_id,
            'tags': tags
    }
    requests.post(f'{host}/api/item/update', json=data)
    return

