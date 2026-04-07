# -*- coding: utf-8 -*-
from django.apps import AppConfig


class CustomerCnConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.customer_cn'
    label = 'customer_cn'
    verbose_name = '国内客户'
