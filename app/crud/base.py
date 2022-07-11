#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/7/12
@Author  : dilless
@Site    : 
@File    : base
@Software: PyCharm
"""
from typing import Optional, Dict, Any, List, Sequence

import pymysql

FetchOneType = Dict[str, Any]
FetchAllType = List[FetchOneType]


class BaseCRUD:
    def __init__(self, host: str, port: int, user: str, password: str, database: Optional[str] = None, charset: Optional[str] = None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset

    def connection(self, *args, **kwargs):
        conn = pymysql.connect(
            *args,
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            **kwargs,
        )
        with conn.cursor() as cursor:
            cursor.execute("SET time_zone='+00:00'")
        return conn

    def fetch_all(self, sql: str, params: Sequence[Any]) -> FetchAllType:
        with self.connection(cursorclass=pymysql.cursors.DictCursor) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                results = cursor.fetchall()

        return results

    def fetch_one(self, sql: str, params: Sequence[Any]) -> FetchOneType:
        with self.connection(cursorclass=pymysql.cursors.DictCursor) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchone()

        return result

    def execute(self, sql: str, params: Sequence[Any]) -> None:
        with self.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
