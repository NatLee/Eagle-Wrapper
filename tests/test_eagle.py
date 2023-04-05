import unittest
from eaglewrapper import Eagle

class TestGetImgInfoWithPath(unittest.TestCase):

    def test_get_img_info_from_lib_path(self):
        eagle = Eagle()
        source_path = ''
        name_start_filters = ['example']
        image_info = eagle.get_img_info_from_lib_path(source_path, name_start_filters)
        self.assertEqual(image_info, [])

if __name__ == '__main__':
    unittest.main()