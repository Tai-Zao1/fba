#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin import router as task_router
from backend.core.conf import settings

v1 = APIRouter(prefix=settings.ADMIN_API_PATH)

v1.include_router(task_router, prefix='/tasks', tags=['任务'])
