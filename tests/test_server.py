from countercat.server import MAX_IMAGE_BYTES


def test_image_size_limit_is_sensible():
    assert MAX_IMAGE_BYTES == 10 * 1024 * 1024
