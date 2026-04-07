# -*- coding: utf-8 -*-
"""
================================================================================
文件：module.py
路径：/home/edo/cimf-v2/modules/customer_cn/module.py
================================================================================

功能说明：
    客户信息（国内）模块信息文件
    
    定义模块的基本信息，供系统扫描和注册使用。

版本：
    - 1.0.0: 初始版本
"""

MODULE_INFO = {
    'id': 'customer_cn',
    'name': '客户信息（国内）',
    'type': 'node',
    'version': '1.0.0',
    'author': 'edouardlicn',
    'description': '国内客户信息管理模块',
    'models': ['CustomerCnFields'],
    'require': [],
    'icon': 'bi-people',
    'permissions': [
        {'key': 'view_others', 'name': '查看别人的内容'},
        {'key': 'edit_others', 'name': '修改别人的内容'},
        {'key': 'delete_others', 'name': '删除别人的内容'},
    ],
    'export_fields': [
        {'name': 'customer_name', 'label': '客户名称', 'type': 'string', 'required': True},
        {'name': 'customer_code', 'label': '客户代码', 'type': 'string', 'required': True},
        {'name': 'customer_type', 'label': '客户类型', 'type': 'fk'},
        {'name': 'enterprise_name', 'label': '企业名称', 'type': 'string'},
        {'name': 'phone1', 'label': '电话1', 'type': 'telephone'},
        {'name': 'email1', 'label': '邮箱1', 'type': 'email'},
        {'name': 'phone2', 'label': '电话2', 'type': 'telephone'},
        {'name': 'email2', 'label': '邮箱2', 'type': 'email'},
        {'name': 'wechat', 'label': '微信', 'type': 'string'},
        {'name': 'dingtalk', 'label': '钉钉', 'type': 'string'},
        {'name': 'address', 'label': '详细地址', 'type': 'string'},
        {'name': 'postal_code', 'label': '邮政编码', 'type': 'string'},
        {'name': 'region', 'label': '省市区', 'type': 'region'},
        {'name': 'industry', 'label': '行业', 'type': 'string'},
        {'name': 'enterprise_type', 'label': '企业类型', 'type': 'fk'},
        {'name': 'registered_capital', 'label': '注册资本', 'type': 'decimal'},
        {'name': 'customer_level', 'label': '客户等级', 'type': 'fk'},
        {'name': 'credit_limit', 'label': '信用额度', 'type': 'decimal'},
        {'name': 'website', 'label': '网站', 'type': 'string'},
        {'name': 'notes', 'label': '备注', 'type': 'string'},
    ],
    'dashboard_stats': True,
    'views': {
        'list': 'customer_list',
        'create': 'customer_create',
        'view': 'customer_view',
        'edit': 'customer_edit',
        'delete': 'customer_delete',
    },
}


def get_install_sql():
    """获取模块安装时执行的 SQL（可选）"""
    return None


def get_uninstall_sql():
    """获取模块卸载时执行的 SQL（可选）"""
    return None
