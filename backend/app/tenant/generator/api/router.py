#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin import router as gen_router
from backend.app.admin import router as gen_business_router
from backend.app.admin import router as gen_model_router
from backend.core.conf import settings

v1 = APIRouter(prefix=f'{settings.ADMIN_API_PATH}/gen', tags=['代码生成'])

v1.include_router(gen_router)
v1.include_router(gen_business_router, prefix='/businesses')
v1.include_router(gen_model_router, prefix='/models')
