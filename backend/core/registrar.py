#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager
from functools import lru_cache

import socketio
from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from starlette.middleware.authentication import AuthenticationMiddleware

from asgi_correlation_id import CorrelationIdMiddleware
from backend.common.exception.exception_handler import register_exception
from backend.common.log import set_customize_logfile, setup_logging
from backend.core.conf import settings
from backend.core.path_conf import STATIC_DIR
from backend.database.db import create_table
from backend.database.redis import redis_client
from backend.middleware.jwt_auth_middleware import JwtAuthMiddleware
from backend.middleware.opera_log_middleware import OperaLogMiddleware
from backend.middleware.state_middleware import StateMiddleware
from backend.plugin.tools import plugin_router_inject
from backend.utils.demo_site import demo_site
from backend.utils.health_check import ensure_unique_route_names, http_limit_callback
from backend.utils.openapi import simplify_operation_ids
from backend.utils.serializers import MsgSpecJSONResponse


@asynccontextmanager
async def register_init(app: FastAPI):
    """
    启动初始化

    :param app: FastAPI 应用实例
    """
    # 创建数据库表
    await create_table()
    # 连接 Redis
    await redis_client.open()
    # 初始化限流器
    await FastAPILimiter.init(
        redis=redis_client,
        prefix=settings.REQUEST_LIMITER_REDIS_PREFIX,
        http_callback=http_limit_callback,
    )

    yield

    # 关闭 Redis 连接
    await redis_client.close()
    # 关闭限流器
    await FastAPILimiter.close()


def create_fastapi_app(
        title: str,
        version: str,
        description: str,
        docs_url: str,
        redoc_url: str,
        openapi_url: str,
        router: object,
) -> FastAPI:
    """
    创建并配置 FastAPI 应用

    :param title: API 文档标题
    :param version: API 版本
    :param description: API 描述
    :param docs_url: Swagger UI URL
    :param redoc_url: ReDoc URL
    :param openapi_url: OpenAPI JSON URL
    :param router: 路由对象
    :return: 配置完成的 FastAPI 应用实例
    """
    app = FastAPI(
        title=title,
        version=version,
        description=description,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        default_response_class=MsgSpecJSONResponse,
        lifespan=register_init,
    )

    # SocketIO
    register_socket_app(app)

    # 日志
    register_logger()

    # 静态文件
    register_static_file(app)

    # 中间件
    register_middleware(app)

    # 路由
    register_router(app, router)

    # 分页
    register_page(app)

    # 全局异常处理
    register_exception(app)

    return app


def register_app():
    """
    注册 Admin 后台应用
    """
    from backend.app.router_admin import router  # 延迟导入避免循环依赖

    return create_fastapi_app(
        title=settings.ADMIN_TITLE,
        version=settings.ADMIN_VERSION,
        description=settings.ADMIN_DESCRIPTION,
        docs_url=settings.ADMIN_DOCS_URL,
        redoc_url=settings.ADMIN_REDOC_URL,
        openapi_url=settings.ADMIN_OPENAPI_URL,
        router=router,
    )


def register_app2():
    """
    注册商家后台应用
    """
    from backend.app.router_tenant import router  # 延迟导入避免循环依赖

    return create_fastapi_app(
        title=settings.STORE_TITLE,
        version=settings.STORE_VERSION,
        description=settings.STORE_DESCRIPTION,
        docs_url=settings.STORE_DOCS_URL,
        redoc_url=settings.STORE_REDOC_URL,
        openapi_url=settings.STORE_OPENAPI_URL,
        router=router,
    )


def register_logger() -> None:
    """
    系统日志配置
    """
    setup_logging()
    set_customize_logfile()


def register_static_file(app: FastAPI):
    """
    挂载静态文件（仅在开发模式下启用）

    :param app: FastAPI 应用实例
    """
    if settings.ADMIN_STATIC_FILES:
        from fastapi.staticfiles import StaticFiles

        app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')


def register_middleware(app: FastAPI):
    """
    注册中间件

    :param app: FastAPI 应用实例
    """
    # 操作日志中间件
    app.add_middleware(OperaLogMiddleware)
    # JWT 认证中间件
    app.add_middleware(
        AuthenticationMiddleware, backend=JwtAuthMiddleware(), on_error=JwtAuthMiddleware.auth_exception_handler
    )
    # 访问日志中间件（可选）
    if settings.MIDDLEWARE_ACCESS:
        from backend.middleware.access_middleware import AccessMiddleware

        app.add_middleware(AccessMiddleware)
    # 状态中间件
    app.add_middleware(StateMiddleware)
    # 请求 ID 中间件
    app.add_middleware(CorrelationIdMiddleware, validator=False)
    # CORS 中间件（可选）
    if settings.MIDDLEWARE_CORS:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
            expose_headers=settings.CORS_EXPOSE_HEADERS,
        )


def register_router(app: FastAPI, router: object):
    """
    注册路由

    :param app: FastAPI 应用实例
    :param router: 路由对象
    """
    dependencies = [Depends(demo_site)] if settings.DEMO_MODE else None

    # 插件路由注入（单例模式确保只执行一次）
    inject_plugin_routers()

    app.include_router(router, dependencies=dependencies)

    # 确保路由名称唯一
    ensure_unique_route_names(app)
    simplify_operation_ids(app)


@lru_cache()
def inject_plugin_routers():
    """
    单例模式：确保插件路由仅注入一次
    """
    plugin_router_inject()


def register_page(app: FastAPI):
    """
    注册分页查询

    :param app: FastAPI 应用实例
    """
    add_pagination(app)


def register_socket_app(app: FastAPI):
    """
    注册 SocketIO 应用

    :param app: FastAPI 应用实例
    """
    sio = lazy_load_socketio()

    socket_app = socketio.ASGIApp(
        socketio_server=sio,
        other_asgi_app=app,
        socketio_path='/ws/socket.io',
    )
    app.mount('/ws', socket_app)


@lru_cache()
def lazy_load_socketio():
    """
    延迟加载 SocketIO
    """
    from backend.common.socketio.server import sio

    return sio