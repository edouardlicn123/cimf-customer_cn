# 客户信息（国内）模块技术规范

> 文档版本：1.1  
> 创建日期：2026-04-28  
> 最后更新：2026-04-28

---

## 一、模块概述

### 1.1 功能定位

`customer_cn` 是国内客户信息管理模块，用于管理中国大陆地区的客户信息。相比海外客户模块 (`customer`)，本模块针对国内业务场景进行了优化，支持省市县三级联动地址选择、微信/钉钉联系方式等功能。

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| 省市县联动 | 支持中国行政区划三级联动选择 |
| 双联系方式 | 电话、邮箱、微信号、钉钉号多渠道联系 |
| 企业信用 | 注册资本、信用额度等企业资质管理 |
| 数据导入导出 | 支持 CSV/Excel 格式批量操作 |
| 权限控制 | 细粒度权限管理，支持查看/编辑/删除他人数据 |

### 1.3 与 customer（海外）模块对比

| 对比项 | customer（海外） | customer_cn（国内） |
|--------|------------------|---------------------|
| 地址字段 | 国家/城市/地址 | 省/市/区/详细地址 |
| 行政区划 | 国家选择器 | 省市县三级联动 |
| 即时通讯 | LinkedIn、Twitter 等 | 微信、钉钉 |
| 税务信息 | Tax ID、VAT | 营业执照号（待扩展） |
| 时区支持 | 多时区 | 中国标准时间 (CST) |

---

## 二、目录结构

```
customer_cn/
├── __init__.py              # 包初始化
├── apps.py                  # Django App 配置
├── admin.py                 # Django Admin 配置 (44行)
├── models.py                # 数据模型 (80行)
├── module.py                # 模块信息配置 (82行)
├── services.py              # 业务服务层 (249行)
├── views.py                 # 视图函数 (336行)
├── urls.py                  # URL 路由配置 (18行)
├── sample_data.py           # 样本数据 (355行)
├── migrations/              # 数据库迁移
│   └── __init__.py
├── templates/               # 模板目录
│   ├── list_cn.html         # 列表页
│   ├── view_cn.html         # 详情页
│   ├── edit_cn.html         # 编辑页（新建/编辑共用）
│   └── customer_cn/
│       └── dashboard_card.html  # 首页卡片
└── docs/                    # 技术文档
    └── README.md            # 本文档
```

---

## 三、数据模型

### 3.1 模型结构

```python
class CustomerCnFields(models.Model):
    """国内客户字段表"""
    
    # 关联节点（必需）
    node = models.OneToOneField(Node, on_delete=models.CASCADE)
    
    # 基础信息
    customer_name = CharField(max_length=200, unique=True)
    customer_code = CharField(max_length=50, unique=True, blank=True, null=True)
    customer_type = ForeignKey(TaxonomyItem)  # 客户类型
    enterprise_name = CharField(max_length=200)
    
    # 联系方式
    phone1/phone2 = CharField(max_length=20)
    email1/email2 = EmailField()
    wechat = CharField(max_length=50)         # 微信号
    dingtalk = CharField(max_length=50)      # 钉钉号
    
    # 地址信息
    region = JSONField()                      # 省市区 JSON
    address = CharField(max_length=200)       # 详细地址
    postal_code = CharField(max_length=10)   # 邮政编码
    
    # 企业信息
    industry = CharField(max_length=50)      # 所属行业
    enterprise_type = ForeignKey(TaxonomyItem)  # 企业性质
    registered_capital = DecimalField(15,2)  # 注册资本
    customer_level = ForeignKey(TaxonomyItem) # 客户等级
    credit_limit = DecimalField(15,2)        # 信用额度
    website = URLField(max_length=200)       # 网站
    
    notes = TextField()                       # 备注
    created_at/updated_at = DateTimeField()   # 时间戳
```

### 3.2 字段说明表

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `node` | OneToOneField | 是 | 关联 Node 节点 |
| `customer_name` | CharField(200) | 是 | 客户名称（唯一） |
| `customer_code` | CharField(50) | 否 | 客户代码（自动生成） |
| `customer_type` | FK(TaxonomyItem) | 否 | 客户类型 |
| `enterprise_name` | CharField(200) | 否 | 企业名称 |
| `phone1` | CharField(20) | 否 | 电话1 |
| `email1` | EmailField | 否 | 邮箱1 |
| `phone2` | CharField(20) | 否 | 电话2 |
| `email2` | EmailField | 否 | 邮箱2 |
| `wechat` | CharField(50) | 否 | 微信号 |
| `dingtalk` | CharField(50) | 否 | 钉钉号 |
| `region` | JSONField | 否 | 省市区（联动数据） |
| `address` | CharField(200) | 否 | 详细地址 |
| `postal_code` | CharField(10) | 否 | 邮政编码 |
| `industry` | CharField(50) | 否 | 所属行业 |
| `enterprise_type` | FK(TaxonomyItem) | 否 | 企业性质 |
| `registered_capital` | DecimalField(15,2) | 否 | 注册资本 |
| `customer_level` | FK(TaxonomyItem) | 否 | 客户等级 |
| `credit_limit` | DecimalField(15,2) | 否 | 信用额度 |
| `website` | URLField(200) | 否 | 网站 |
| `notes` | TextField | 否 | 备注 |

### 3.3 region 字段数据结构

```json
{
    "province": "44",
    "city": "4403",
    "district": "440305"
}
```

---

## 四、服务层 (CustomerCnService)

### 4.1 方法说明

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `get_list()` | search, enterprise_type_id, customer_level_id | List[CustomerCnFields] | 获取客户列表，支持搜索和筛选 |
| `get_by_id()` | customer_id: int | CustomerCnFields | 根据ID获取客户 |
| `get_by_node_id()` | node_id: int | CustomerCnFields | 根据节点ID获取客户 |
| `create()` | user, data: Dict | CustomerCnFields | 创建客户（自动生成代码） |
| `update()` | customer_id, user, data | CustomerCnFields | 更新客户 |
| `delete()` | customer_id: int | bool | 删除客户 |
| `get_count()` | - | int | 获取客户总数 |
| `get_recent_count()` | days: int = 7 | int | 获取最近N天新增数 |
| `get_region_display()` | region: dict | str | 获取省市区显示文本 |
| `get_exportable_fields()` | - | List[Dict] | 获取可导出字段配置 |
| `init_sample_data()` | - | int | 初始化样本数据 |

### 4.2 使用示例

```python
from modules.customer_cn.services import CustomerCnService

# 获取列表（支持搜索和筛选）
customers = CustomerCnService.get_list(
    search='科技',
    enterprise_type_id=1,
    customer_level_id=2
)

# 创建客户
data = {
    'customer_name': '深圳某某科技公司',
    'customer_type_id': 1,
    'region': {'province': '44', 'city': '4403', 'district': '440305'},
    'phone1': '0755-12345678',
    'wechat': 'wx_id_123',
}
customer = CustomerCnService.create(request.user, data)

# 获取省市区显示文本
region_text = CustomerCnService.get_region_display(customer.region)
# 返回: "广东省 深圳市 南山区"
```

---

## 五、视图层

### 5.1 URL 路由配置

```python
# modules/customer_cn/urls.py
app_name = 'customer_cn'

urlpatterns = [
    path('', views.node_list, name='list'),
    path('create/', views.node_create, name='create'),
    path('<int:node_id>/', views.node_view, name='view'),
    path('<int:node_id>/edit/', views.node_edit, name='edit'),
    path('<int:node_id>/delete/', views.node_delete, name='delete'),
    path('api/stats/', views.api_stats, name='api_stats'),
]
```

### 5.2 URL 与视图对照表

| URL | 视图函数 | 模板 | 说明 |
|-----|----------|------|------|
| `/modules/customer_cn/` | `node_list` | `list_cn.html` | 列表页 |
| `/modules/customer_cn/create/` | `node_create` | `edit_cn.html` | 新建页 |
| `/modules/customer_cn/{node_id}/` | `node_view` | `view_cn.html` | 详情页 |
| `/modules/customer_cn/{node_id}/edit/` | `node_edit` | `edit_cn.html` | 编辑页 |
| `/modules/customer_cn/{node_id}/delete/` | `node_delete` | - | 删除（重定向） |
| `/modules/customer_cn/api/stats/` | `api_stats` | - | 统计API |

### 5.3 分页参数

列表页使用 Django Paginator 分页，每页 10 条记录。

| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码（默认 1） |
| `search` | string | 客户名称/企业名称搜索 |
| `enterprise_type` | int | 企业性质筛选 |
| `customer_level` | int | 客户等级筛选 |

**分页响应数据：**

```python
{
    'page_obj': Paginator,        # 分页对象
    'current_page': int,          # 当前页码
    'total_pages': int,           # 总页数
    'has_prev': bool,            # 是否有上一页
    'has_next': bool,            # 是否有下一页
    'prev_page': int,            # 上一页页码
    'next_page': int,            # 下一页页码
}
```

### 5.4 表单处理流程

**GET 请求（新建/编辑页面）：**
1. 获取当前节点类型
2. 加载词汇表数据（客户类型、客户等级、企业性质）
3. 如为编辑模式，加载现有客户数据
4. 渲染表单模板

**POST 请求（表单提交）：**
1. 解析 region JSON 字段
2. 从 POST 数据构建客户数据字典
3. 调用 `CustomerCnService.create()` 或 `update()`
4. 处理异常并返回消息
5. 重定向到列表页或详情页

```python
# 表单数据处理示例
if request.method == 'POST':
    region_data = {}
    region_json = request.POST.get('region', '{}')
    if region_json:
        region_data = json.loads(region_json)
    
    data = {
        'customer_name': request.POST.get('customer_name', '').strip(),
        'region': region_data,
        # ... 其他字段
    }
    
    try:
        CustomerCnService.create(request.user, data)
        messages.success(request, '国内客户创建成功')
        return redirect('modules:customer_cn:list')
    except Exception as e:
        messages.error(request, str(e))
```

### 5.5 API 响应格式

**api_stats 接口：**

```json
// GET /modules/customer_cn/api/stats/
{
    "success": true,
    "data": {
        "total": 150,      // 客户总数
        "recent": 12       // 最近7天新增数
    }
}
```

### 5.6 权限控制

```python
def check_customer_cn_permission(user, node, permission_type):
    """权限检查逻辑"""
    if user.is_admin:
        return True, None
    if node.created_by_id == user.id:
        return True, None
    # 检查 view_others/edit_others/delete_others 权限
```

| 权限 key | 说明 |
|----------|------|
| `node.customer_cn.view_others` | 查看他人创建的客户 |
| `node.customer_cn.edit_others` | 编辑他人创建的客户 |
| `node.customer_cn.delete_others` | 删除他人创建的客户 |

---

## 六、模板

### 6.1 模板列表

| 模板 | 说明 | 代码行数 |
|------|------|----------|
| `list_cn.html` | 客户列表页 | ~240行 |
| `view_cn.html` | 客户详情页 | ~280行 |
| `edit_cn.html` | 新建/编辑表单页 | ~440行 |
| `customer_cn/dashboard_card.html` | 首页卡片 | ~30行 |

### 6.2 模板继承结构

```
base.html
  └── frame_node.html
        ├── list_cn.html      # 列表页
        ├── view_cn.html      # 详情页
        └── edit_cn.html     # 编辑页（新建/编辑共用）
```

### 6.3 省市区联动字段

模板中使用省市县联动字段：

```html
<!-- 省市区联动 HTML 结构 -->
<div class="region-select-widget">
    <div class="row">
        <div class="col-md-4">
            <select class="form-select region-province">
                <option value="">请选择省份</option>
            </select>
        </div>
        <div class="col-md-4">
            <select class="form-select region-city" disabled>
                <option value="">请先选择省份</option>
            </select>
        </div>
        <div class="col-md-4">
            <select class="form-select region-district" disabled>
                <option value="">请先选择城市</option>
            </select>
        </div>
    </div>
    <!-- 隐藏字段存储 JSON 数据 -->
    <input type="hidden" name="region" value="{}">
</div>
```

---

## 七、module.py 配置

```python
MODULE_INFO = {
    'id': 'customer_cn',
    'name': '客户信息（国内）',
    'type': 'node',
    'version': '1.1.3',
    'models': ['CustomerCnFields'],
    'require': [],
    'icon': 'bi-people',
    'frontpage_card_clickable': True,
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
    'dashboard_cards': [
        {
            'id': 'customer_cn_card',
            'name': '国内客户卡片',
            'template': 'customer_cn/dashboard_card.html',
            'color_start': '#ffa348',
            'color_end': '#ffa348',
        }
    ],
    'views': {
        'list': 'customer_list',
        'create': 'customer_create',
        'view': 'customer_view',
        'edit': 'customer_edit',
        'delete': 'customer_delete',
    },
}
```

---

## 八、数据导入导出

### 8.1 导出字段配置

`export_fields` 定义了可导出字段，共 18 个字段：

| 字段名 | 中文名 | 类型 | 必填 |
|--------|--------|------|------|
| customer_name | 客户名称 | string | 是 |
| customer_code | 客户代码 | string | 是 |
| customer_type | 客户类型 | fk | 否 |
| enterprise_name | 企业名称 | string | 否 |
| phone1 | 电话1 | telephone | 否 |
| email1 | 邮箱1 | email | 否 |
| phone2 | 电话2 | telephone | 否 |
| email2 | 邮箱2 | email | 否 |
| wechat | 微信 | string | 否 |
| dingtalk | 钉钉 | string | 否 |
| address | 详细地址 | string | 否 |
| postal_code | 邮政编码 | string | 否 |
| region | 省市区 | region | 否 |
| industry | 行业 | string | 否 |
| enterprise_type | 企业类型 | fk | 否 |
| registered_capital | 注册资本 | decimal | 否 |
| customer_level | 客户等级 | fk | 否 |
| credit_limit | 信用额度 | decimal | 否 |
| website | 网站 | string | 否 |
| notes | 备注 | string | 否 |

### 8.2 region 字段导入格式

```json
{
    "province": "44",
    "city": "4403",
    "district": "440305"
}
```

---

## 九、表单验证与错误处理

### 9.1 字段验证规则

| 字段 | 验证规则 | 错误提示 |
|------|----------|----------|
| `customer_name` | 必填，最大 200 字符，唯一 | "客户名称不能为空" |
| `customer_code` | 可选，最大 50 字符，唯一，自动生成 | 唯一性冲突时提示 |
| `email1/email2` | EmailField 格式验证 | "请输入有效的邮箱地址" |
| `website` | URLField 格式验证 | "请输入有效的网址" |
| `phone1/phone2` | 无格式限制（可为空） | - |
| `region` | JSON 格式，包含 province/city/district | JSON 解析失败时使用空值 |
| `registered_capital` | DecimalField(15,2) | 格式错误时为 None |
| `credit_limit` | DecimalField(15,2) | 格式错误时为 None |

### 9.2 异常处理

```python
# 创建客户异常处理
try:
    CustomerCnService.create(request.user, data)
    messages.success(request, '国内客户创建成功')
except ValueError as e:
    messages.error(request, str(e))
except Exception as e:
    messages.error(request, f'创建失败: {str(e)}')

# 更新客户异常处理
try:
    CustomerCnService.update(customer.id, request.user, data)
    messages.success(request, '国内客户更新成功')
except Exception as e:
    messages.error(request, str(e))

# 删除客户异常处理
try:
    CustomerCnService.delete(node_id)
    messages.success(request, '国内客户已删除')
except Exception as e:
    messages.error(request, f'删除失败: {str(e)}')
```

### 9.3 错误消息类型

| 消息类型 | 使用场景 | 样式 |
|----------|----------|------|
| `messages.success` | 操作成功 | Bootstrap 绿色提示 |
| `messages.error` | 操作失败 | Bootstrap 红色提示 |
| `messages.warning` | 警告信息 | Bootstrap 黄色提示 |
| `messages.info` | 提示信息 | Bootstrap 蓝色提示 |

---

## 十、依赖关系

### 10.1 模块依赖

| 依赖 | 说明 |
|------|------|
| `core.node` | 节点核心系统 |
| `core.TaxonomyItem` | 词汇表项 |
| `core.services.TaxonomyService` | 词汇表服务 |
| `modules.customer_cn.models` | 本模块模型 |

### 10.2 词汇表依赖

| 词汇表 | Slug | 用途 |
|--------|------|------|
| 客户类型 | `customer_type` | 客户分类 |
| 客户等级 | `customer_level` | 客户分级 |
| 企业性质 | `economic_type` 或 `enterprise_nature` | 企业分类 |

---

## 十一、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.1.3 | 2026-04-28 | 补充表单验证、API响应、分页参数等详细说明 |
| 1.1.0 | 2026-04-12 | 移动到 modules/customer_cn/ 目录 |
| 1.0.0 | 2026-03-12 | 初始版本 |

---

## 十二、相关文档

| 文档 | 说明 |
|------|------|
| [A02_模块技术规范](../../docs/技术规范/A02_模块技术规范.md) | 模块系统实现指南 |
| [A03_省市县联动字段技术规范](../../docs/技术规范/A03_省市县联动字段技术规范.md) | 省市县三级联动设计 |
| [A04_模板开发规范](../../docs/技术规范/A04_模板开发规范.md) | Jinja2 模板开发规范 |