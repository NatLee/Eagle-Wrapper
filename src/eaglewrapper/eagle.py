'''
Eagle class
'''
from typing import Optional, List, Dict, Any
import datetime
from pathlib import Path
import json
import concurrent.futures
import requests
from loguru import logger

class ImageData:
    """
    A class to represent image data for adding images to Eagle.

    Attributes:
        url (str): Required. The URL of the image to be added. Supports http, https, and base64.
        name (str): Required. The name of the image to be added.
        website (str): The address of the image source.
        tags (list): Tags for the image.
        annotation (str): The annotation for the image.
        modificationTime (int): The creation date of the image. Can be used to alter the image's sorting order in Eagle.
        headers (dict): Optional. Customize the HTTP headers properties. Can be used to bypass security on certain websites.
    """
    def __init__(self, url: str, name: str, website: str = '', tags: list = None, annotation: str = '', modificationTime: int = None, headers: dict = None):
        """
        Initializes the ImageData instance with the given attributes.

        Args:
            url (str): Required. The URL of the image to be added. Supports http, https, and base64.
            name (str): Required. The name of the image to be added.
            website (str, optional): The address of the image source. Defaults to an empty string.
            tags (list, optional): Tags for the image. Defaults to an empty list.
            annotation (str, optional): The annotation for the image. Defaults to an empty string.
            modificationTime (int, optional): The creation date of the image. Can be used to alter the image's sorting order in Eagle. Defaults to None.
            headers (dict, optional): Optional. Customize the HTTP headers properties. Can be used to bypass security on certain websites. Defaults to an empty dictionary.
        
        Raises:
            ValueError: If the URL or name is empty.
        """
        if tags is None:
            tags = []
        if headers is None:
            headers = {}

        if not url:
            raise ValueError("URL cannot be empty.")
        if not name:
            raise ValueError("Name cannot be empty.")

        self.url = url
        self.name = name
        self.website = website
        self.tags = tags
        self.annotation = annotation
        self.modificationTime = modificationTime
        self.headers = headers

    def to_dict(self) -> dict:
        return self.__dict__


class Eagle:
    def __init__(self, domain='http://localhost', port=41595):
        self.domain = domain
        self.port = port
        self.host = f'{domain}:{port}'

    def check_success(self, response) -> bool:
        """
        Check if the API response status is 'success'.
        
        Args:
            response (Response): The response object from an API call.

        Returns:
            bool: True if the status is 'success', otherwise False.
        """
        status = response.json().get('status')
        if status != 'success':
            return False
        return True

    # =================================================
    # NOT IN API methods
    # =================================================

    def get_img_info_from_lib_path(self, library_path: str, name_start_filters=[], max_workers=4) -> list:
        """
        Get all images' information (metadata) from the path of the source library.

        For example, there is a path of a library at '/path/to/your/test.library'.

        Args:
            library_path (str): The path of the source library.
            name_start_filters (list, optional): A list of name prefixes to filter images. Defaults to an empty list.
            max_workers (int, optional): The number of concurrent workers. Defaults to 4.

        Returns:
            list: A list of dictionaries containing the metadata of the images.
        """

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
                executor.submit(load_id, meta_path): meta_path for meta_path in Path(library_path).glob('**/metadata.json')
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

    def set_tag_with_id(self, item_id: int, tags: list) -> dict:
        """
        Set tags to an image with its ID by using `update` API.

        API DOC: https://api.eagle.cool/item/update

        Args:
            item_id (int): The ID of the image to be updated.
            tags (list): A list of tags to be associated with the image.

        Returns:
            dict: A dictionary containing the result information of the updated image.
        """
        return self.update_item(item_id, tags)

    def get_img_list_info(self, max_image_number: int, name_start_filter='') -> list:
        """
        Get a list of images' information up to the specified maximum number of images.

        API DOC: https://api.eagle.cool/item/list

        Args:
            max_image_number (int): The maximum number of images to retrieve.
            name_start_filter (str, optional): A string to filter images by name prefix. Defaults to an empty string.

        Returns:
            list: A list of dictionaries containing the information of the retrieved images.
        """
        resp = requests.get(f'{self.host}/api/item/list?limit={max_image_number}')
        data = resp.json().get('data')
        if name_start_filter != '':
            data = [d for d in data if d.get('name').startswith(name_start_filter)]
        return data

    # =================================================
    # Application methods
    # =================================================

    def get_application_info(self) -> dict:
        """
        Get detailed information on the Eagle App currently running.

        API DOC: https://api.eagle.cool/application/info

        Returns:
            dict: A dictionary containing the detailed information on the Eagle App, such as version, buildVersion, execPath, and platform.
        """
        resp = requests.get(f'{self.host}/api/application/info')
        return resp.json().get('data')

    # =================================================
    # Image (Item) methods
    # =================================================

    def add_from_url(self, url: str, name: str, tags=[], website='', annotation='', modification_time: int = None, folder_id: str = None, headers: dict = None) -> bool:
        """
        Add a new image or materials from the given URL.

        API DOC: https://api.eagle.cool/item/add-from-url

        Args:
            url (str): The URL of the image or materials to be added.
            name (str): The name to be assigned to the item.
            tags (list, optional): A list of tags to be associated with the item. Defaults to an empty list.
            website (str, optional): The website where the image or materials are from. Defaults to ''.
            annotation (str, optional): Any additional annotation or description for the item. Defaults to ''.
            modification_time (int, optional): The creation date of the image.
            folder_id (str, optional): If this parameter is defined, the image will be added to the corresponding folder.
            headers (dict, optional): Customize the HTTP headers properties, this could be used to circumvent the security of certain websites.

        Returns:
            bool: A flag.
        """

        data = ImageData(
            url=url,
            name=name,
            website=website,
            tags=tags,
            annotation=annotation,
            modificationTime=modification_time,
            headers=headers
        ).to_dict()

        if folder_id is not None:
            data["folderId"] = folder_id

        resp = requests.post(f'{self.host}/api/item/addFromURL', json=data)
        return self.check_success(resp)

    def add_from_urls(self, items: list, folder_id: str = None) -> bool:
        """
        Add multiple images from URLs to Eagle.

        API DOC: https://api.eagle.cool/item/add-from-urls

        Args:
            items (list): The array object made up of multiple items. Each item is a dictionary with keys:
                - url (str): Required, the URL of the image to be added. Supports http, https, base64.
                - name (str): Required, the name of the image to be added.
                - website (str, optional): The address of the source of the image.
                - annotation (str, optional): The annotation for the image.
                - tags (list, optional): Tags for the image.
                - modificationTime (int, optional): The creation date of the image.
                - headers (dict, optional): Customize the HTTP headers properties.
            folder_id (str, optional): If the parameter is defined, images will be added to the corresponding folder.

        Returns:
            bool: A flag.
        """
        items_ = []

        for item in items:
            item_ = ImageData(
                url=item['url'],
                name=item['name'],
                website=item['website'],
                tags=item['tags'],
                annotation=item['annotation'],
                modificationTime=item['modification_time'],
                headers=item['headers']
            ).to_dict()
            items_.append(item_)

        data = {"items": items_}

        if folder_id is not None:
            data["folderId"] = folder_id

        resp = requests.post(f'{self.host}/api/item/addFromURLs', json=data)
        return self.check_success(resp)

    def add_from_path(self, path: str, name: str, website: Optional[str] = None,
                      annotation: Optional[str] = None, tags: Optional[List[str]] = None,
                      folder_id: Optional[str] = None) -> bool:
        """
        Add a local file to Eagle.

        API DOC: https://api.eagle.cool/item/add-from-path

        Args:
            path (str): Required, the path of the local file.
            name (str): Required, the name of the image to be added.
            website (str, optional): The address of the source of the image.
            annotation (str, optional): The annotation for the image.
            tags (List[str], optional): Tags for the image.
            folder_id (str, optional): If this parameter is defined, the image will be added to the corresponding folder.

        Returns:
            bool: A flag.
        """

        data = ImageData(
            url=path,
            name=name,
            website=website,
            tags=tags,
            annotation=annotation
        ).to_dict()

        data['path'] = data['url']
        del data['url']

        data["folderId"] = folder_id

        resp = requests.post(f'{self.host}/api/item/addFromPath', json=data)
        return resp.json()

    def add_from_paths(self, items: List[Dict], folder_id: Optional[str] = None) -> bool:
        """
        Add multiple local files to Eagle.

        API DOC: https://api.eagle.cool/item/add-from-paths

        Args:
            items (List[Dict]): A list of dictionaries containing the following keys:
                - path (str): The path of the local file.
                - name (str): The name of the image to be added.
                - website (str, optional): The address of the source of the image.
                - annotation (str, optional): The annotation for the image.
                - tags (List[str], optional): Tags for the image.
            folder_id (str, optional): If this parameter is defined, the images will be added to the corresponding folder.

        Returns:
            bool: A flag.
        """
        items_ = []

        for item in items:
            item_ = ImageData(
                url=item["path"],
                name=item["name"],
                website=item["website"],
                tags=item["tags"],
                annotation=item["annotation"]
            ).to_dict()
            item_['path'] = item_['url']
            del item_['url']
            items_.append(item_)

        data = {"items": items_}

        if folder_id is not None:
            data["folderId"] = folder_id

        resp = requests.post(f'{self.host}/api/item/addFromPaths', json=data)
        return self.check_success(resp)

    def add_bookmark(self, url: str, name: str, tags: List[str] = None,
                     thumbnail_base64: str = None, modification_time: int = None,
                     folder_id: str = None) -> bool:
        """
        Save the link in the URL form to Eagle.

        API DOC: https://api.eagle.cool/item/add-bookmark

        Args:
            url (str): The link of the image to be saved. Supports http, https, base64.
            name (str): The name of the image to be added.
            tags (List[str], optional): Tags for the image.
            thumbnail_base64 (str, optional): The thumbnail of the bookmark. Must be in base64 format.
            modification_time (int, optional): The creation date of the images. The parameter can be used to alter the
                                               images' sorting order in Eagle.
            folder_id (str, optional): If this parameter is defined, the image will be added to the corresponding folder.

        Returns:
            bool: A flag.
        """
        data = {
            "url": url,
            "name": name,
            "tags": tags or [],
            "base64": thumbnail_base64,
            "modificationTime": modification_time,
            "folderId": folder_id
        }
        resp = requests.post(f'{self.host}/api/item/addBookmark', json=data)

        return self.check_success(resp)

    def get_item_info(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get properties of the specified file, including the file name, tags, categorizations, folders, dimensions, etc.

        API DOC: https://api.eagle.cool/item/info

        Args:
            item_id (str): ID of the file.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the properties of the specified file or None if unsuccessful.
        """

        params = {'id': item_id}
        resp = requests.get(f'{self.host}/api/item/info', params=params)

        if not self.check_success(resp):
            return None
        return resp.json().get('data')

    def get_thumbnail_path(self, item_id: str) -> Optional[str]:
        """
        Get the path of the thumbnail of the specified file.

        API DOC: https://api.eagle.cool/item/thumbnail

        Args:
            item_id (str): ID of the file.

        Returns:
            Optional[str]: The thumbnail path of the specified file or None if unsuccessful.
        """
        params = {'id': item_id}
        resp = requests.get(f'{self.host}/api/item/thumbnail', params=params)

        if not self.check_success(resp):
            return None
        return resp.json().get('data')

    def list_items(self, limit: int = 200, offset: int = 0, order_by: Optional[str] = None, keyword: Optional[str] = None, ext: Optional[str] = None, tags: Optional[List[str]] = None, folders: Optional[List[str]] = None) -> dict:
        """
        Get items that match the filter condition.

        API DOC: https://api.eagle.cool/item/list

        Args:
            limit (int): The number of items to be displayed. The default number is 200.
            offset (int): Offset a collection of results from the api. Start with 0.
            order_by (Optional[str]): The sorting order. CREATEDATE, FILESIZE, NAME, RESOLUTION, add a minus sign for descending order: -FILESIZE.
            keyword (Optional[str]): Filter by the keyword.
            ext (Optional[str]): Filter by the extension type, e.g.: jpg, png.
            tags (Optional[List[str]]): Filter by tags.
            folders (Optional[List[str]]): Filter by Folders.

        Returns:
            dict: A dictionary containing the filtered items and their information.
        """
        params = {'limit': limit, 'offset': offset}
        if order_by:
            params['orderBy'] = order_by
        if keyword:
            params['keyword'] = keyword
        if ext:
            params['ext'] = ext
        if tags:
            params['tags'] = ','.join(tags)
        if folders:
            params['folders'] = ','.join(folders)

        resp = requests.get(f'{self.host}/api/item/list', params=params)

        return resp.json().get('data')

    def move_to_trash(self, item_ids: List[str]) -> bool:
        """
        Move items to trash.

        API DOC: https://api.eagle.cool/item/api-item-movetotrash

        Args:
            item_ids (List[str]): A list of item IDs to be moved to trash.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        data = {"itemIds": item_ids}
        resp = requests.post(f'{self.host}/api/item/moveToTrash', json=data)

        return self.check_success(resp)

    def refresh_palette(self, item_id: str) -> bool:
        """
        Re-analysis the color of the file. When changes to the original file were made,
        you can call this function to refresh the Color Analysis.

        API DOC: https://api.eagle.cool/item/refresh-palette

        Args:
            item_id (str): The item's ID.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        data = {"id": item_id}
        resp = requests.post(f'{self.host}/api/item/refreshPalette', json=data)

        return self.check_success(resp)

    def refresh_thumbnail(self, item_id: str) -> bool:
        """
        Re-generate the thumbnail of the file used to display in the List. When changes to
        the original file were made, you can call this function to re-generate the thumbnail,
        the color analysis will also be made.

        API DOC: https://api.eagle.cool/item/refresh-thumbnail

        Args:
            item_id (str): The item's ID.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        data = {"id": item_id}
        resp = requests.post(f'{self.host}/api/item/refreshThumbnail', json=data)

        return self.check_success(resp)

    def update_item(self, item_id: str, tags: Optional[List[str]] = None, annotation: Optional[str] = None, url: Optional[str] = None, star: Optional[int] = None) -> dict:
        """
        Modify data of specified fields of the item.

        API DOC: https://api.eagle.cool/item/update

        Args:
            item_id (str): Required, the ID of the item to be modified.
            tags (list): Optional, tags.
            annotation (str): Optional, annotations.
            url (str): Optional, the source url.
            star (int): Optional, ratings.

        Returns:
            dict: Updated item data.
        """
        data = {"id": item_id}

        if tags is not None:
            data["tags"] = tags

        if annotation is not None:
            data["annotation"] = annotation

        if url is not None:
            data["url"] = url

        if star is not None:
            data["star"] = star

        resp = requests.post(f'{self.host}/api/item/update', json=data)

        if not self.check_success(resp):
            raise Exception("[Eagle] Failed to update the item.")

        return resp.json().get("data")

    # =================================================
    # Folder methods
    # =================================================

    def create_folder(self, folder_name: str, parent_id=None) -> dict:
        """
        Create a folder. The created folder will be placed at the bottom of the folder list of the current library.

        API DOC: https://api.eagle.cool/folder/create

        Args:
            folder_name (str): The name of the folder to be created.
            parent_id (int, optional): The ID of the parent folder. If not provided, the created folder will be at the top level. Defaults to None.
        
        Returns:
            dict: A dictionary containing the result information of the created folder.
        """

        data = {
            'folderName': folder_name,
        }
        if parent_id is not None:
            data['parent'] = parent_id

        resp = requests.post(f'{self.host}/api/folder/create', json=data)
        return resp.json().get('data')

    def rename_folder(self, folder_id: str, new_name: str) -> dict:
        """
        Rename the specified folder.

        API DOC: https://api.eagle.cool/folder/rename

        Args:
            folder_id (str): The ID of the folder to be renamed.
            new_name (str): The new name for the folder.
        
        Returns:
            dict: A dictionary containing the result information of the renamed folder.
        """
        data = {
            'folderId': folder_id,
            'newName': new_name,
        }

        resp = requests.post(f'{self.host}/api/folder/rename', json=data)
        return resp.json().get('data')

    def update_folder(self, folder_id: str, new_name: str = None, new_description: str = None, new_color: str = None) -> dict:
        """
        Update the specified folder.

        API DOC: https://api.eagle.cool/folder/update

        Args:
            folder_id (str): The ID of the folder to be updated.
            new_name (str, optional): The new name for the folder. Defaults to None.
            new_description (str, optional): The new description for the folder. Defaults to None.
            new_color (str, optional): The new color for the folder. Valid options are "red", "orange", "green", "yellow", "aqua", "blue", "purple", "pink". Defaults to None.
        
        Returns:
            dict: A dictionary containing the result information of the updated folder.
        """
        data = {
            'folderId': folder_id,
        }
        if new_name is not None:
            data['newName'] = new_name
        if new_description is not None:
            data['newDescription'] = new_description
        if new_color is not None:
            data['newColor'] = new_color

        resp = requests.post(f'{self.host}/api/folder/update', json=data)
        return resp.json().get('data')

    def list_folders(self) -> dict:
        """
        Get the list of folders of the current library.

        API DOC: https://api.eagle.cool/folder/list

        Returns:
            list: A list of dictionaries containing the folder information.
        """

        resp = requests.get(f'{self.host}/api/folder/list')
        return resp.json().get('data')

    def get_recent_folders(self) -> dict:
        """
        Get the list of recently used folders by the user.

        API DOC: https://api.eagle.cool/folder/list-recent

        Returns:
            dict: A dictionary containing the status and data of the recently used folders.
        """
        resp = requests.get(f'{self.host}/api/folder/listRecent')
        return resp.json().get('data')

    # =================================================
    # Library methods
    # =================================================

    def get_library_info(self) -> dict:
        """
        Get detailed information of the currently running library. This function can be used to obtain details
        such as All Folders, All Smart Folders, All Tag Groups, Quick Access, etc.

        API DOC: https://api.eagle.cool/library/info

        Returns:
            dict: A dictionary containing detailed information about the currently running library.
        """
        resp = requests.get(f'{self.host}/api/library/info')
        return resp.json().get('data')

    def get_library_history(self) -> list:
        """
        Get the list of libraries recently opened by the Application.

        API DOC: https://api.eagle.cool/library/history

        Returns:
            list: A list containing the paths of recently opened libraries.
        """
        resp = requests.get(f'{self.host}/api/library/history')
        return resp.json().get('data')

    def switch_library(self, library_path: str) -> bool:
        """
        Switch the library currently opened by Eagle.

        API DOC: https://api.eagle.cool/library/switch

        Args:
            library_path (str): The path of the library to switch to.

        Returns:
            bool: A flag.
        """
        data = {
            "libraryPath": library_path
        }
        resp = requests.post(f'{self.host}/api/library/switch', json=data)
        return self.check_success(resp)

