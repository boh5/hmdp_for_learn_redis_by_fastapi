# hmdp_for_learn_redis_by_fastapi

这是[黑马程序员的 redis 课程实战篇](https://www.bilibili.com/video/BV1cr4y1671t?p=24)的代码的 python 实现。由于我主要使用
python 做后台开发，因此在看课程的时候用 python 实现了一份和原 java 代码几乎同样功能的 python 后端。

如果有其他童鞋也在学该课程，希望能帮助到你。😀

代码很多地方不够完善，特别随项目增长，很多地方需要重构的，我都没精力去搞了。如果有任何疑问或致命 bug 欢迎讨论。🥂

### 依赖( requirements.txt ) ⚓

1. fastapi==0.78.0 : 后端框架
2. sqlmodel==0.0.6 : orm，从版本号可看出该框架截至 2022-07-29 尚不十分成熟
3. pymysql==1.0.2 : orm backend
4. uvicorn==0.18.2 : ASGI 服务器，fastapi 依赖此启动
5. itsdangerous==2.1.2 : Starlette 的 SessionMiddleware 依赖
6. starsessions==1.2.3 : 实现基于内存的 session. (fastapi 默认只支持基于 cookies 的 session)
7. aioredis[hiredis]==2.0.1 : asyncio 的 redis 库，后弃用，由于发现该库以完全在 redis-py 中实现
8. pytest==7.1.2 : 想写测试的，后来算了 😜
9. python-multipart==0.0.5 : fastapi FileUpload 依赖
10. redis[hiredis]==4.3.4 : redis
11. types-redis==4.3.11 : pycharm 中 `from redis import asyncio` 会出警告，安装该库可解决

### 项目结构 🧱

大致和 fastapi 作者提供的 [Full Stack FastAPI PostgreSQL](https://github.com/tiangolo/full-stack-fastapi-postgresql)
模板中的 backend 结构一致

### 分支 🕎

##### 每个章节的代码提交到独立的分支中，[master](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/master) 含所有代码

| 章节序号 | 章节名称            | 分支                                                                                                                                          |
|------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| 1    | 短信登录            | [redis_based_login](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/redis_based_login)                                      |
| 2    | 商户查询缓存          | [query_cache](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/query_cache)                                                  |
| 3    | 优惠卷秒杀           | [seckill](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/seckill)                                                          |
| 4    | 分布式锁            | [distributed-lock](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/distributed-lock)                                        |
| 5    | 分布式锁-redission  | [distributed-lock](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/distributed-lock) ( python 没有类似 redission 的库，因此未完全实现该章节) |
| 6    | 秒杀优化            | [seckill-optimize](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/seckill-optimize)                                        |
| 7    | Redis消息队列       | [redis-mq](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/redis-mq)                                                        |
| 8    | 达人探店            | [blog](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/blog)                                                                |
| 9    | 好友关注            | [follow](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/follow)                                                            |
| 10   | 附近商户            | [geo](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/geo)                                                                  |
| 11   | 用户签到            | [user-sign](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/user-sign)                                                      |
| 12   | UV统计            | [uv-log](https://github.com/dilless/hmdp_for_learn_redis_by_fastapi/tree/uv-log)                                                            |
