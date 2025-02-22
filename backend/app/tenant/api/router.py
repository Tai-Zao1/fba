#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.tenant.api.v1.auth import router as auth_router
from backend.app.tenant.api.v1.sys import router as sys_router
from backend.app.tenant.api.v1.common import router as common_router
from backend.core.conf import settings

tenant = APIRouter(prefix=settings.STORE_API_PATH)

tenant.include_router(auth_router)
tenant.include_router(sys_router)
tenant.include_router(common_router)
