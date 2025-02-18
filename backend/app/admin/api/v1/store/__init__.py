#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.api.v1.store.store import router as store_router

router = APIRouter(prefix='/store')

router.include_router(store_router, prefix='/user', tags=['商户信息'])
