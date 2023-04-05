# Eagle Wrapper


[![PyPI pyversions](https://img.shields.io/pypi/pyversions/EagleWrapper.svg)](https://pypi.python.org/pypi/EagleWrapper/)[![PyPI implementation](https://img.shields.io/pypi/implementation/EagleWrapper.svg)](https://pypi.python.org/pypi/EagleWrapper/)

[![Test](https://github.com/NatLee/Eagle-Wrapper/actions/workflows/test.yml/badge.svg)](https://github.com/NatLee/Eagle-Wrappger/actions/workflows/test.yml)[![Release](https://github.com/NatLee/Eagle-Wrapper/actions/workflows/release.yml/badge.svg)](https://github.com/NatLee/Eagle-Wrapper/actions/workflows/release.yml)

[![PyPI status](https://img.shields.io/pypi/status/EagleWrapper.svg)](https://pypi.python.org/pypi/EagleWrapper/)[![PyPI license](https://img.shields.io/pypi/l/EagleWrapper.svg)](https://pypi.python.org/pypi/EagleWrapper/)

[![PyPI version fury.io](https://badge.fury.io/py/EagleWrapper.svg)](https://pypi.python.org/pypi/EagleWrapper/)

[![PyPI download month](https://img.shields.io/pypi/dm/EagleWrapper.svg)](https://pypi.python.org/pypi/EagleWrapper/)[![PyPI download week](https://img.shields.io/pypi/dw/EagleWrapper.svg)](https://pypi.python.org/pypi/EagleWrapper/)[![PyPI download day](https://img.shields.io/pypi/dd/EagleWrapper.svg)](https://pypi.python.org/pypi/EagleWrapper/)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

This is a python wrapper for a image and design management software named Eagle.

Its official website is https://eagle.cool/.


## API Reference

This wrapper is reference from [Eagle Official API documentation](https://api.eagle.cool/)

Some APIs are not available in this wrapper because they are not implemented.

## Usage

```bash
pip install EagleWrapper
```

> Notice: You need open Eagle when using this wrapper or it cannot find your host of Eagle.

## Method

- get_img_info_from_lib_path

> This is a method of searching file `metadata.json` of images from directly library folder, so it will fast than using `get_img_list_info`.

```python
eagle = Eagle()
source_path = '/my/lib/path/example/測試.library' # your library path
name_start_filters = ['example', 'ぼ'] # your filters with the image name
image_info = eagle.get_img_info_from_lib_path(source_path, name_start_filters)
```

- add_from_url

```python
url = 'https://s.yimg.com/ny/api/res/1.2/1ui_Mvv4s2Gtmr4uZdP.mA--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTY4NDtjZj13ZWJw/https://s.yimg.com/os/creatr-uploaded-images/2022-11/1f7132d0-5e6a-11ed-b7bd-ba3b4a3aed4f'
name = 'ぼっち・ざ・ろっく！'
tags = ['ぼっち', 'ろっく']
website = 'https://tw.news.yahoo.com/bocchi-the-rock-071607480.html'
annotation = 'This is an example ;)'
eagle.add_from_url(url, name, tags, website, annotation)
```

This output will show in Eagle:

![add-from-url](./doc/add-from-url.png)

- get_img_list_info

List image INFO which name starting with `ぼ` in limit 10.

```python
from eagle_wrapper import Eagle
eagle = Eagle()
max_image_number = 10 # maximum number of images for searching
name_start_filter = 'ぼ' # search filters
image_list_info = eagle.get_img_list_info(max_image_number, name_start_filter)
```

The output is:

```json
[{
    "id": "LG3YCGZW5QH1B",
    "name": "ぼっち・ざ・ろっく！",
    "size": 219336,
    "btime": 1680715050765,
    "mtime": 1680715050880,
    "ext": "jpg",
    "tags": ["ぼっち", "ろっく"],
    "folders": [],
    "isDeleted": false,
    "url": "https://tw.news.yahoo.com/bocchi-the-rock-071607480.html",
    "annotation": "This is an example ;)",
    "modificationTime": 1680715050761,
    "height": 684,
    "width": 960,
    "noThumbnail": true,
    "palettes": [
        {
            "color": [196, 172, 154],
            "ratio": 33,
            "$$hashKey": "object:1775"
        },
        {
            "color": [48, 43, 43],
            "ratio": 26,
            "$$hashKey": "object:1776"
        },
        ...
        {
            "color": [225, 204, 205],
            "ratio": 2.66,
            "$$hashKey": "object:1783"
        }
    ]
}]
```

## Contributor

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center"><a href="https://github.com/NatLee"><img src="https://avatars.githubusercontent.com/u/10178964?v=3?s=100" width="100px;" alt="Nat Lee"/><br /><sub><b>Nat Lee</b></sub></a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## License

[MIT](LICENSE)








