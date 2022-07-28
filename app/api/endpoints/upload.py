"""
    upload
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
import os.path

from fastapi import APIRouter, UploadFile, Query

import schemas
from core.config import settings
from utils.upload import get_new_filename

router = APIRouter()


@router.post('/blog',
             response_model=schemas.GenericResponseModel)
async def upload_image(
        *,
        file: UploadFile
):
    original_filename = file.filename
    filename = get_new_filename(original_filename)
    try:
        with open(os.path.join(settings.IMAGE_UPLOAD_DIR, filename), 'wb') as f:
            f.write(file.file.read())
    except IOError:
        return schemas.GenericResponseModel(success=False, error_msg='上传失败')
    return schemas.GenericResponseModel(data='/' + filename)


@router.get('/blog/delete',
            response_model=schemas.GenericResponseModel)
async def delete_image(
        *,
        name: str = Query()
):
    filepath = os.path.join(settings.IMAGE_UPLOAD_DIR, name[6:])
    if not os.path.exists(filepath):
        return schemas.GenericResponseModel(success=False, error_msg='错误的文件名')
    os.remove(filepath)
    return schemas.GenericResponseModel()
