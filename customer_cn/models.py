# -*- coding: utf-8 -*-
"""
国内客户模型
"""

from django.db import models
from core.node.models import Node


class CustomerCnFields(models.Model):
    """国内客户字段表"""
    
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
        related_name='customer_cn_fields',
        verbose_name='关联节点'
    )
    
    customer_name = models.CharField(max_length=200, unique=True, verbose_name='客户名称')
    customer_code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='客户代码')
    customer_type = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_type_customer_cn',
        verbose_name='客户类型'
    )
    enterprise_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='企业名称')
    
    phone1 = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话1')
    email1 = models.EmailField(blank=True, null=True, verbose_name='邮箱1')
    phone2 = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话2')
    email2 = models.EmailField(blank=True, null=True, verbose_name='邮箱2')
    
    region = models.JSONField(blank=True, null=True, verbose_name='省市区')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='详细地址')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='邮政编码')
    
    wechat = models.CharField(max_length=50, blank=True, null=True, verbose_name='微信号')
    dingtalk = models.CharField(max_length=50, blank=True, null=True, verbose_name='钉钉号')
    
    industry = models.CharField(max_length=50, blank=True, null=True, verbose_name='所属行业')
    enterprise_type = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enterprise_type_customer_cn',
        verbose_name='企业性质'
    )
    registered_capital = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='注册资本')
    
    customer_level = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_level_customer_cn',
        verbose_name='客户等级'
    )
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='信用额度')
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name='网站')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'customer_cn_fields'
        verbose_name = '国内客户'
        verbose_name_plural = '国内客户'
    
    @property
    def creator(self):
        return self.node.created_by if hasattr(self, 'node') and self.node else None
    
    def __str__(self):
        return self.customer_name
