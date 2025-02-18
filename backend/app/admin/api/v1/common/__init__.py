#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.api.v1.common.address import router as address_router

router = APIRouter(prefix='/common')

router.include_router(address_router, prefix='/address', tags=['通用方法'])
