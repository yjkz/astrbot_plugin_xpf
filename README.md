# XIV Party Finder

[![AstrBot](https://img.shields.io/badge/AstrBot-v4.16+-blue)](https://astrbot.app)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

AstrBot 插件 · 查询 FFXIV 集招募信息，支持按大区、副本、关键词筛选。

![预览](README.jpg)

---

## 功能特性

- **多种查询方式**：列表、搜索、大区筛选、副本筛选、类别筛选
- **详细招募信息**：查看队伍槽位、装等要求、剩余时间等
- **双模式展示**：纯文本 + 图片卡片（深色主题）
- **职能/职业中文翻译**：所有英文缩写自动转为中文
- **槽位状态显示**：清晰展示已满/待补状态

---

## 安装

1. 在 AstrBot WebUI → 插件管理 → 从 GitHub 安装
2. 输入仓库地址：`yjkz/astrbot_plugin_xpf`
3. 安装完成后在插件配置中调整参数

---

## 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `api_base_url` | string | `https://xivpf.littlenightmare.top/api` | API 地址 |
| `default_datacenter` | string | `""` | 默认大区（留空查全部） |
| `default_per_page` | int | `5` | 每页显示数量（最大 100） |
| `result_as_image` | bool | `false` | 是否以图片形式发送结果 |

---

## 指令

| 指令 | 说明 | 示例 |
|------|------|------|
| `/pf help` | 显示帮助信息 | |
| `/pf list [大区] [页码]` | 查看最新招募 | `/pf list 豆豆柴 2` |
| `/pf search <关键词> [页码]` | 搜索招募 | `/pf search 绝` |
| `/pf dc <大区> [页码]` | 按大区筛选 | `/pf dc 猫小胖` |
| `/pf duty <副本ID> [页码]` | 按副本筛选 | `/pf duty 1006,1007` |
| `/pf cat <类别> [页码]` | 按类别筛选 | `/pf cat 高难度任务` |
| `/pf detail <ID>` | 查看招募详情 | `/pf detail 124630` |

**支持的类别**：高难度任务、迷宫探索、讨伐歼灭战、团队副本、PvP、行会令、深层迷宫、寻宝、金碟游乐场、优雷卡、异闻迷宫、混沌同盟任务、随机任务

---

## 效果预览

**文本模式**
```
#1 空心剂 (萌芽池)
  其他 ─ 无
  █░░░░░░░ 1/8 │ 3分钟
  ⇔跨服
  「【萌芽沙15-8】地中海南岸风无招待挂机店，喜欢您来。」
  └ 陆行鸟 │ ID:128896
```

**详情模式**
```
────────────────────────────
  从命
────────────────────────────
  其他 │ 其他
  无

  陆行鸟 / 宇宙和音 (宇宙和音)
  跨服: ⇔跨服 │ 新人: ✘
  装等: 无要求

  ███░░░░░ 3/8 │ 5分钟
  目标: 通关副本

────────────────────────────
  队伍槽位
────────────────────────────
  1. [DPS] 舞者
  2. [坦克] 战士
  3. [坦克] 暗黑骑士
  4. [任意] 待补
```

---

## 致谢

本插件查询数据来源于 [LittleNightmare/remote-party-finder](https://github.com/LittleNightmare/remote-party-finder) 项目，感谢其提供的 FFXIV 集招募 API 服务。

前端参考：[remote-party-finder-frontend](https://github.com/Cindy-Master/remote-party-finder-frontend)

---

## 注意事项

- **图片模式**：图片生成功能依赖 AstrBot 内置的 T2I（Text-to-Image）服务，该服务由 AstrBot 官方维护。当服务不可用时，插件会自动降级为文本模式输出。如需稳定使用图片模式，请确保 T2I 服务正常运行。
- **跨服标识**：`⇔跨服` 表示该招募在同一数据中心内所有服务器可见。
- **API 速率**：请勿过于频繁查询，以免触发 API 限流。

---

## 开发

```bash
git clone https://github.com/yjkz/astrbot_plugin_xpf.git
cd astrbot_plugin_xpf
pip install -r requirements.txt
```

将插件放入 AstrBot 的 `data/plugins/` 目录即可加载。

---

## License

MIT
