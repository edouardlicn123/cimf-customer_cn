# -*- coding: utf-8 -*-
"""
================================================================================
文件：views.py
路径：/home/edo/cimf-v2/modules/customer_cn/views.py
================================================================================

功能说明：
    国内客户模块视图

版本：
    - 1.0: 从 modules/views.py 拆分

依赖：
    - django: Web 框架
    - modules.customer_cn.services: 国内客户服务
    - core.node.services: Node服务
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from core.node.services import NodeTypeService, NodeService
from modules.customer_cn.services import CustomerCnService
from core.services import PermissionService


def safe_int(value: str, default=None):
    """安全地将字符串转换为整数"""
    if not value:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def check_customer_cn_permission(user, node, permission_type: str):
    """检查国内客户节点操作权限"""
    if user.is_admin:
        return True, None
    
    is_creator = node.created_by_id == user.id
    
    if is_creator:
        return True, None
    
    perm_map = {
        'view': 'node.customer_cn.view_others',
        'edit': 'node.customer_cn.edit_others',
        'delete': 'node.customer_cn.delete_others',
    }
    
    perm = perm_map.get(permission_type)
    if perm and PermissionService.has_permission(user, perm):
        return True, None
    
    return False, f'您没有权限{permission_type}别人的国内客户信息'


@login_required
def node_list(request):
    """国内客户列表"""
    node_type = NodeTypeService.get_by_slug('customer_cn')
    if not node_type:
        from django.http import Http404
        node_type = NodeTypeService.get_by_slug_including_inactive('customer_cn')
        if node_type:
            raise Http404(f'节点类型 "{node_type.name}" 已禁用')
        raise Http404('节点类型不存在')
    
    search = request.GET.get('search', '')
    enterprise_type_filter = request.GET.get('enterprise_type', '')
    customer_level_filter = request.GET.get('customer_level', '')
    node_types = NodeTypeService.get_all()
    
    from core.services import TaxonomyService
    enterprise_type_tax = TaxonomyService.get_taxonomy_by_slug('enterprise_nature')
    enterprise_types = [{'id': c.id, 'name': c.name} for c in TaxonomyService.get_items(enterprise_type_tax.id)] if enterprise_type_tax else []
    customer_level_tax = TaxonomyService.get_taxonomy_by_slug('customer_level')
    customer_levels = [{'id': c.id, 'name': c.name} for c in TaxonomyService.get_items(customer_level_tax.id)] if customer_level_tax else []
    
    enterprise_type_id = safe_int(enterprise_type_filter)
    customer_level_id = safe_int(customer_level_filter)
    
    customers = CustomerCnService.get_list(
        search if search else None,
        enterprise_type_id=enterprise_type_id,
        customer_level_id=customer_level_id
    )
    
    page_num = request.GET.get('page', 1)
    paginator = Paginator(customers, 10)
    page_obj = paginator.get_page(page_num)
    
    return render(request, 'list_cn.html', {
        'node_type': node_type,
        'node_types': node_types,
        'customers': page_obj.object_list,
        'search': search,
        'active_section': 'customer_cn',
        'filter_enterprise_type': enterprise_type_filter,
        'filter_customer_level': customer_level_filter,
        'enterprise_types': enterprise_types,
        'customer_levels': customer_levels,
        'page_obj': page_obj,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_prev': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    })


@login_required
def node_create(request):
    """创建国内客户"""
    node_type = NodeTypeService.get_by_slug('customer_cn')
    if not node_type:
        from django.http import Http404
        node_type = NodeTypeService.get_by_slug_including_inactive('customer_cn')
        if node_type:
            raise Http404(f'节点类型 "{node_type.name}" 已禁用')
        raise Http404('节点类型不存在')
    
    node_types = NodeTypeService.get_all()
    
    from core.services import TaxonomyService
    import json
    
    customer_type_tax = TaxonomyService.get_taxonomy_by_slug('customer_type')
    customer_types = TaxonomyService.get_items(customer_type_tax.id) if customer_type_tax else []
    customer_level_tax = TaxonomyService.get_taxonomy_by_slug('customer_level')
    customer_levels = TaxonomyService.get_items(customer_level_tax.id) if customer_level_tax else []
    enterprise_type_tax = TaxonomyService.get_taxonomy_by_slug('economic_type')
    enterprise_types = TaxonomyService.get_items(enterprise_type_tax.id) if enterprise_type_tax else []
    
    if request.method == 'POST':
        region_data = {}
        region_json = request.POST.get('region', '{}')
        if region_json:
            try:
                region_data = json.loads(region_json)
            except json.JSONDecodeError:
                pass
        
        data = {
            'customer_name': request.POST.get('customer_name', '').strip(),
            'customer_code': request.POST.get('customer_code', '').strip() or None,
            'customer_type_id': request.POST.get('customer_type') or None,
            'enterprise_name': request.POST.get('enterprise_name', '').strip() or None,
            'phone1': request.POST.get('phone1', '').strip() or None,
            'email1': request.POST.get('email1', '').strip() or None,
            'phone2': request.POST.get('phone2', '').strip() or None,
            'email2': request.POST.get('email2', '').strip() or None,
            'region': region_data,
            'address': request.POST.get('address', '').strip() or None,
            'postal_code': request.POST.get('postal_code', '').strip() or None,
            'wechat': request.POST.get('wechat', '').strip() or None,
            'dingtalk': request.POST.get('dingtalk', '').strip() or None,
            'industry': request.POST.get('industry', '').strip() or None,
            'enterprise_type_id': request.POST.get('enterprise_type') or None,
            'registered_capital': request.POST.get('registered_capital') or None,
            'customer_level_id': request.POST.get('customer_level') or None,
            'credit_limit': request.POST.get('credit_limit') or None,
            'website': request.POST.get('website', '').strip() or None,
            'notes': request.POST.get('notes', '').strip() or None,
        }
        
        try:
            CustomerCnService.create(request.user, data)
            messages.success(request, '国内客户创建成功')
            return redirect('modules:customer_cn:list')
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'edit_cn.html', {
        'node_type': node_type,
        'node_types': node_types,
        'customer': None,
        'active_section': 'customer_cn',
        'customer_types': customer_types,
        'customer_levels': customer_levels,
        'enterprise_types': enterprise_types,
    })


@login_required
def node_view(request, node_id: int):
    """查看国内客户"""
    node = NodeService.get_by_id(node_id)
    if not node:
        from django.http import Http404
        raise Http404('节点不存在')
    
    has_perm, error_msg = check_customer_cn_permission(request.user, node, 'view')
    if not has_perm:
        messages.error(request, error_msg)
        return redirect('modules:customer_cn:list')
    
    node_types = NodeTypeService.get_all()
    
    customer = CustomerCnService.get_by_node_id(node_id)
    if not customer:
        messages.error(request, '国内客户不存在')
        return redirect('modules:customer_cn:list')
    
    region_display = CustomerCnService.get_region_display(customer.region) if customer and customer.region else ''
    
    return render(request, 'view_cn.html', {
        'node_type': node.node_type,
        'node_types': node_types,
        'node': node,
        'customer': customer,
        'region_display': region_display,
        'active_section': 'customer_cn',
    })


@login_required
def node_edit(request, node_id: int):
    """编辑国内客户"""
    node = NodeService.get_by_id(node_id)
    if not node:
        from django.http import Http404
        raise Http404('节点不存在')
    
    has_perm, error_msg = check_customer_cn_permission(request.user, node, 'edit')
    if not has_perm:
        messages.error(request, error_msg)
        return redirect('modules:customer_cn:view', node_id=node_id)
    
    node_types = NodeTypeService.get_all()
    
    customer = CustomerCnService.get_by_node_id(node_id)
    if not customer:
        messages.error(request, '国内客户不存在')
        return redirect('modules:customer_cn:list')
    
    from core.services import TaxonomyService
    import json
    
    customer_type_tax = TaxonomyService.get_taxonomy_by_slug('customer_type')
    customer_types = TaxonomyService.get_items(customer_type_tax.id) if customer_type_tax else []
    customer_level_tax = TaxonomyService.get_taxonomy_by_slug('customer_level')
    customer_levels = TaxonomyService.get_items(customer_level_tax.id) if customer_level_tax else []
    enterprise_type_tax = TaxonomyService.get_taxonomy_by_slug('economic_type')
    enterprise_types = TaxonomyService.get_items(enterprise_type_tax.id) if enterprise_type_tax else []
    
    if request.method == 'POST':
        region_data = {}
        region_json = request.POST.get('region', '{}')
        if region_json:
            try:
                region_data = json.loads(region_json)
            except json.JSONDecodeError:
                pass
        
        data = {
            'customer_name': request.POST.get('customer_name', '').strip(),
            'customer_code': request.POST.get('customer_code', '').strip() or None,
            'customer_type_id': request.POST.get('customer_type') or None,
            'enterprise_name': request.POST.get('enterprise_name', '').strip() or None,
            'phone1': request.POST.get('phone1', '').strip() or None,
            'email1': request.POST.get('email1', '').strip() or None,
            'phone2': request.POST.get('phone2', '').strip() or None,
            'email2': request.POST.get('email2', '').strip() or None,
            'region': region_data,
            'address': request.POST.get('address', '').strip() or None,
            'postal_code': request.POST.get('postal_code', '').strip() or None,
            'wechat': request.POST.get('wechat', '').strip() or None,
            'dingtalk': request.POST.get('dingtalk', '').strip() or None,
            'industry': request.POST.get('industry', '').strip() or None,
            'enterprise_type_id': request.POST.get('enterprise_type') or None,
            'registered_capital': request.POST.get('registered_capital') or None,
            'customer_level_id': request.POST.get('customer_level') or None,
            'credit_limit': request.POST.get('credit_limit') or None,
            'website': request.POST.get('website', '').strip() or None,
            'notes': request.POST.get('notes', '').strip() or None,
        }
        
        try:
            CustomerCnService.update(customer.id, request.user, data)
            messages.success(request, '国内客户更新成功')
            return redirect('modules:customer_cn:view', node_id=node_id)
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'edit_cn.html', {
        'node_type': node.node_type,
        'node_types': node_types,
        'node': node,
        'customer': customer,
        'active_section': 'customer_cn',
        'customer_types': customer_types,
        'customer_levels': customer_levels,
        'enterprise_types': enterprise_types,
    })


@login_required
def node_delete(request, node_id: int):
    """删除国内客户"""
    node = NodeService.get_by_id(node_id)
    if node:
        has_perm, error_msg = check_customer_cn_permission(request.user, node, 'delete')
        if not has_perm:
            messages.error(request, error_msg)
        else:
            CustomerCnService.delete(node_id)
            messages.success(request, '国内客户已删除')
    else:
        messages.error(request, '节点不存在')
    
    return redirect('modules:customer_cn:list')


@login_required
def api_stats(request):
    """获取客户统计信息"""
    from django.http import JsonResponse
    from modules.customer_cn.services import CustomerCnService
    
    total = CustomerCnService.get_count()
    recent = CustomerCnService.get_recent_count(days=7)
    
    return JsonResponse({
        'success': True,
        'data': {
            'total': total,
            'recent': recent,
        }
    })
