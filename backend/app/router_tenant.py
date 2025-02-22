#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.tenant.api.router import tenant as tenant_v1

'''
store路由
'''
router = APIRouter()
router.include_router(tenant_v1)
