"""
    follow
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
from typing import List

from fastapi import APIRouter, Path, Depends
from pydantic import parse_obj_as
from sqlmodel import Session, select, col

import models
import schemas
from api import deps
from db.mysql import engine
from utils.redis_ import FollowUtils

router = APIRouter()


@router.get('/common/{user_id}',
            response_model=schemas.GenericResponseModel)
async def get_common_follows(
        *,
        target_user_id: int = Path(),
        user: schemas.UserBaseModel = Depends(deps.verify_user),
):
    common_ids = await FollowUtils.get_common_follow(user.id, target_user_id)
    if not common_ids:
        return schemas.GenericResponseModel()
    with Session(engine) as sess:
        common_users = sess.exec(select(models.User).where(col(models.User.id).in_(common_ids))).all()
        users = parse_obj_as(List[schemas.UserBaseModel], common_users)
    return schemas.GenericResponseModel(data=users)


@router.get('/or/not/{follow_user_id}',
            response_model=schemas.GenericResponseModel)
async def is_followed(
        *,
        follow_user_id: int = Path(),
        user: schemas.UserBaseModel = Depends(deps.verify_user)
):
    with Session(engine) as sess:
        follow_model = sess.exec(select(models.Follow)
                                 .where(models.Follow.user_id == user.id)
                                 .where(models.Follow.follow_user_id == follow_user_id)).all()
    return schemas.GenericResponseModel(data=len(follow_model) > 0)


@router.put('/{follow_user_id}/{is_follow}',
            response_model=schemas.GenericResponseModel)
async def follow(
        *,
        follow_user_id: int = Path(),
        is_follow: bool = Path(),
        user: schemas.UserBaseModel = Depends(deps.verify_user)
):
    if is_follow:
        with Session(engine) as sess:
            exists = sess.exec(select(models.Follow)
                               .where(models.Follow.user_id == user.id)
                               .where(models.Follow.follow_user_id == follow_user_id)).first()
            if exists:
                return schemas.GenericResponseModel(success=False, error_msg='不能重复关注')

            follow_model = models.Follow(
                user_id=user.id,
                follow_user_id=follow_user_id,
            )
            sess.add(follow_model)
            try:
                sess.commit()
            except Exception as e:
                print(e)
            else:
                await FollowUtils.add_follow(user.id, follow_user_id)
    else:
        with Session(engine) as sess:
            follow_model = sess.exec(select(models.Follow)
                                     .where(models.Follow.user_id == user.id)
                                     .where(models.Follow.follow_user_id == follow_user_id)).first()
            if follow_model:
                sess.delete(follow_model)
                try:
                    sess.commit()
                except Exception as e:
                    print(e)
                else:
                    await FollowUtils.remove_follow(user.id, follow_user_id)
    return schemas.GenericResponseModel()
