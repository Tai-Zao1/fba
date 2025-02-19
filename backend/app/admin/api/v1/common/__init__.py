#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.api.v1.common.address import router as address_router
from backend.app.admin.api.v1.common.captcha import router as captcha_router

router = APIRouter(prefix='/common')

router.include_router(address_router, prefix='/address', tags=['通用方法'])
router.include_router(captcha_router, prefix='/captcha', tags=['通用方法'])
