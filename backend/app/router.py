#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.api.router import v1 as admin_v1
from backend.app.tenant.api.router import v1 as tenant_v1
from backend.app.admin.task.api.router import v1 as task_v1

'''
admin路由
'''
router = APIRouter()

router.include_router(admin_v1)
# router.include_router(generator_v1)
router.include_router(task_v1)

'''
store路由
'''
router2 = APIRouter()
router2.include_router(tenant_v1)
