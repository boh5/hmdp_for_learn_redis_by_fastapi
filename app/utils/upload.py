"""
    upload
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/28
"""
import os.path
import uuid

from core.config import settings


def get_new_filename(original_filename):
    suffix = original_filename.split('.')[-1]

    # 生成目录
    name = uuid.uuid4().hex
    name_hash = hash(name)
    d1 = name_hash & 0xf
    d2 = (name_hash >> 4) & 0xf

    file_dir = os.path.join(settings.IMAGE_UPLOAD_DIR, f'blogs/{d1}/{d2}')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    return f'blogs/{d1}/{d2}/{name}.{suffix}'


if __name__ == '__main__':
    print(get_new_filename('a.jag'))
