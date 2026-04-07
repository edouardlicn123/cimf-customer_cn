# 国内客户模块 (Customer CN Module)

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](./)
[![Django](https://img.shields.io/badge/django-6.0+-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](./LICENSE)

> 用于 [仙芙CIMF](https://github.com/anomalyco/cimf) 系统的国内客户信息管理模块。

本模块是 [cimf](https://github.com/anomalyco/cimf) 主项目的插件式模块之一，位于主项目的 `modules/customer_cn/` 目录。与海外客户模块（`customer_ab`）配合使用，实现国内外客户信息的分类管理。

## 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [数据模型](#数据模型)
- [路由接口](#路由接口)
- [权限配置](#权限配置)
- [词汇表配置](#词汇表配置)
- [示例数据](#示例数据)
- [项目结构](#项目结构)
- [依赖](#依赖)
- [更新日志](#更新日志)

---

## 功能特性

- **客户信息管理** - 完整的 CRUD 操作，支持增删改查
- **多维度筛选** - 按企业性质、客户等级、关键词搜索
- **客户代码自动生成** - 自动生成 `CCN` + 6位数字格式（如 `CCN123456`）
- **权限控制** - 基于角色的细粒度权限管理
- **仪表盘统计** - 提供 API 接口用于仪表盘数据展示
- **省市区地址管理** - 支持省市区 JSON 字段，配套三级联动选择器
- **双联系方式** - 支持两个电话 + 两个邮箱记录
- **社交账号管理** - 支持微信、钉钉等即时通讯账号

---

## 快速开始

### 模块信息

| 属性 | 值 |
|------|-----|
| 模块Slug | `customer_cn` |
| 节点类型 | 国内客户 |
| 主项目路径 | `modules/customer_cn/` |

### 安装

模块已集成到 CIMF 主项目中，初始化时自动安装：

```bash
# 进入主项目目录
cd /path/to/cimf

# 初始化数据库（自动安装所有模块）
python init_db.py --with-data
```

### 手动安装

```bash
# 进入 Django shell
python manage.py shell

# 安装模块
from core.node.services import ModuleService
ModuleService.install_module('customer_cn')
```

### 访问

初始化完成后，访问 `/customer_cn/` 即可进入国内客户管理页面。

---

## 数据模型

### CustomerCnFields

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `node` | OneToOneField | ✅ | 关联 Node 节点 |
| `customer_name` | CharField(200) | ✅ | 客户名称（唯一） |
| `customer_code` | CharField(50) | - | 客户代码（唯一，自动生成） |
| `customer_type` | ForeignKey | - | 客户类型（词汇表） |
| `enterprise_name` | CharField(200) | - | 企业名称 |
| **联系方式** | | | |
| `phone1` | CharField(20) | - | 电话1 |
| `email1` | EmailField | - | 邮箱1 |
| `phone2` | CharField(20) | - | 电话2 |
| `email2` | EmailField | - | 邮箱2 |
| `wechat` | CharField(50) | - | 微信号 |
| `dingtalk` | CharField(50) | - | 钉钉号 |
| **地址信息** | | | |
| `region` | JSONField | - | 省市区 `{ province, city, district }` |
| `address` | CharField(200) | - | 详细地址 |
| `postal_code` | CharField(10) | - | 邮政编码 |
| **企业信息** | | | |
| `industry` | CharField(50) | - | 所属行业 |
| `enterprise_type` | ForeignKey | - | 企业性质（词汇表） |
| `registered_capital` | DecimalField(15,2) | - | 注册资本（万元） |
| **客户等级** | | | |
| `customer_level` | ForeignKey | - | 客户等级（词汇表） |
| `credit_limit` | DecimalField(15,2) | - | 信用额度（元） |
| `website` | URLField(200) | - | 企业网站 |
| `notes` | TextField | - | 备注 |
| **时间戳** | | | |
| `created_at` | DateTimeField | ✅ | 创建时间（自动） |
| `updated_at` | DateTimeField | ✅ | 更新时间（自动） |

---

## 路由接口

### 页面路由

| 路径 | 方法 | 视图 | 说明 |
|------|------|------|------|
| `/customer_cn/` | GET | `node_list` | 客户列表页（分页） |
| `/customer_cn/create/` | GET/POST | `node_create` | 创建客户 |
| `/customer_cn/<node_id>/` | GET | `node_view` | 查看详情 |
| `/customer_cn/<node_id>/edit/` | GET/POST | `node_edit` | 编辑客户 |
| `/customer_cn/<node_id>/delete/` | POST | `node_delete` | 删除客户 |

### API 接口

| 路径 | 方法 | 说明 | 返回 |
|------|------|------|------|
| `/customer_cn/api/stats/` | GET | 获取统计数据 | `{ success, data: { total, recent } }` |

**统计 API 响应示例：**

```json
{
  "success": true,
  "data": {
    "total": 520,
    "recent": 28
  }
}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `total` | int | 客户总数 |
| `recent` | int | 最近7天新增客户数 |

---

## 权限配置

模块使用 CIMF 系统统一的权限控制机制：

| 权限标识 | 说明 |
|----------|------|
| `node.customer_cn.view_others` | 查看他人的客户信息 |
| `node.customer_cn.edit_others` | 编辑他人的客户信息 |
| `node.customer_cn.delete_others` | 删除他人的客户信息 |

**默认规则：**

- 管理员（`is_admin=True`）拥有所有权限
- 创建者可查看/编辑/删除自己创建的记录
- 非管理员查看/编辑他人数据需配置对应权限

---

## 词汇表配置

模块安装时需要配置以下词汇表（Taxonomy）：

| Slug | 名称 | 用途 | 预设选项示例 |
|------|------|------|-------------|
| `customer_type` | 客户类型 | 客户分类 | 潜在客户、正式客户、战略合作伙伴 |
| `customer_level` | 客户等级 | 客户价值分级 | VIP、A级、B级、C级 |
| `economic_type` / `enterprise_nature` | 企业性质 | 企业所有制类型 | 国有企业、民营企业、外资企业、合资企业 |

**配置方式：**

进入系统管理后台 -> 词汇表管理，创建上述分类并添加选项。

---

## 示例数据

模块提供示例数据初始化功能，用于开发和测试：

### 示例数据内容

`sample_data.py` 包含约 50 条模拟国内客户数据，涵盖：
- 不同客户类型（潜在客户、正式客户等）
- 不同客户等级（VIP、A级、B级等）
- 多个行业（制造业、服务业、科技等）
- 完整联系方式（电话、邮箱、微信）

### 使用方法

```python
# 进入 Django shell
python manage.py shell

# 初始化示例数据
from modules.customer_cn.services import CustomerCnService
count = CustomerCnService.init_sample_data()
print(f"已创建 {count} 条示例数据")
```

---

## 项目结构

```
cimf-customer_cn/           # 模块根目录
├── __init__.py             # 模块初始化
├── apps.py                 # Django App 配置
├── models.py               # 数据模型（CustomerCnFields）
├── services.py             # 业务逻辑层（CustomerCnService）
├── views.py                # 视图控制器
├── urls.py                 # URL 路由
├── admin.py                # Django Admin 配置
├── sample_data.py          # 示例数据
├── LICENSE                 # MIT 许可证
├── README.md               # 本文件
├── migrations/             # 数据库迁移文件
│   ├── __init__.py
│   └── 0001_initial.py
└── templates/               # 模板文件
    ├── list_cn.html        # 列表页
    ├── view_cn.html        # 详情页
    └── edit_cn.html        # 编辑页
```

**在主项目中的路径：**

```
cimf/                       # 主项目根目录
├── modules/
│   ├── __init__.py
│   ├── urls.py
│   └── customer_cn/        # <-- 本模块
│       ├── __init__.py
│       ├── models.py
│       ├── services.py
│       ├── views.py
│       └── ...
```

---

## 依赖

- **Django** 6.0+
- **core** 应用（Node、NodeType、Taxonomy 等核心模型）
- **主项目** cimf（仙芙CIMF）

---

## 更新日志

### 1.0.0 (2026-03-31)

- ✨ 初始版本发布
- ✨ 客户信息 CRUD 功能
- ✨ 多维度筛选（企业性质、客户等级、搜索）
- ✨ 客户代码自动生成（CCN + 6位数字）
- ✨ 省市区地址管理（JSONField + 三级联动）
- ✨ 双联系方式支持（双电话 + 双邮箱）
- ✨ 社交账号管理（微信、钉钉）
- ✨ 权限控制（创建者/他人数据隔离）
- ✨ 仪表盘统计 API
- ✨ 示例数据初始化功能

---

## 相关模块

| 模块 | 说明 |
|------|------|
| [cimf](https://github.com/anomalyco/cimf) | 主项目 - 仙芙CIMF企业内部管理框架 |
| [cimf-resident_info](https://github.com/anomalyco/cimf-resident_info) | 居民信息管理模块 |
| [cimf-customer_ab](https://github.com/anomalyco/cimf-customer_ab) | 海外客户信息管理模块 |
