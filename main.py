import aiohttp
from astrbot.api.event import AstrMessageEvent
from astrbot.api.event import filter as event_filter
from astrbot.api.star import Context, Star
from astrbot.api import logger, AstrBotConfig

PLUGIN_NAME = "astrbot_plugin_xpf"
USER_AGENT = f"{PLUGIN_NAME} (1993369000@qq.com)"

# v1 API 类别中文映射
CATEGORY_NAMES = {
    "None": "其他",
    "HighEndDuty": "高难度任务",
    "Dungeons": "迷宫探索",
    "Trials": "讨伐歼灭战",
    "Raids": "团队副本",
    "PvP": "PvP",
    "Guildhests": "行会令",
    "DeepDungeons": "深层迷宫",
    "TreasureHunt": "寻宝",
    "GoldSaucer": "金碟游乐场",
    "Eureka": "优雷卡",
    "VCDungeonFinder": "异闻迷宫",
    "ChaoticAllianceRaid": "混沌同盟任务",
    "DutyRoulette": "随机任务",
}

# 副本类型中文映射
DUTY_TYPE_NAMES = {
    "Normal": "普通",
    "Roulette": "随机",
    "Raid": "副本",
    "Trial": "讨伐",
    "Dungeon": "迷宫",
    "PvP": "PvP",
    "Other": "其他",
}

# 目标中文映射
OBJECTIVE_NAMES = {
    "DUTY_COMPLETION": "通关副本",
    "PRACTICE": "练习",
    "LOOT": "拾取",
    "NONE": "无",
}

# 条件中文映射
CONDITIONS_NAMES = {
    "NONE": "无",
    "DUTY_COMPLETE": "已完成",
    "MIN_ILVL": "最低装等",
}

# 分配方式中文映射
LOOT_NAMES = {
    "NONE": "无",
    "FREEFORALL": "自由拾取",
    "NEED_GREED": "需求优先",
    "LOOTMASTER": "分配者拾取",
}

# 大区到服务器的映射（国服）
DATACENTER_WORLDS = {
    "莫古力": ["潮风亭", "神拳痕", "白银乡", "白金幻象", "红茶川"],
    "猫小胖": ["紫水栈桥", "延夏", "静语庄园", "摩杜纳", "海猫茶屋"],
    "豆豆柴": ["水晶塔", "银泪湖", "伊修加德", "太阳海岸", "亚马乌罗提"],
    "陆行鸟": ["红玉海", "神意之地", "拉诺西亚", "幻影群岛", "萌芽池"],
}

# 角色图标（文本模式用 Emoji，图片模式用 FFXIV 字体）
ROLE_ICONS_TEXT = {
    "Tank": "🛡",
    "Healer": "💚",
    "DPS": "⚔",
}
ROLE_ICONS_FFXIV = {
    "Tank": " ",
    "Healer": " ",
    "DPS": " ",
}

# 职能颜色
ROLE_COLORS = {
    "Tank": "#3d85c6",
    "Healer": "#6aa84f",
    "DPS": "#cc0000",
}

# 职能中文
ROLE_CN = {
    "Tank": "坦克",
    "Healer": "治疗",
    "DPS": "DPS",
}

# 职业图标 CDN
SDO_ICON_BASE = "https://img.nga.178.com/attachments/mon_202503"
JOB_ICON_URLS = {
    # 坦克
    "PLD": f"{SDO_ICON_BASE}/zjob0.png",
    "WAR": f"{SDO_ICON_BASE}/zjob1.png",
    "DRK": f"{SDO_ICON_BASE}/zjob2.png",
    "GNB": f"{SDO_ICON_BASE}/zjob3.png",
    # 治疗
    "WHM": f"{SDO_ICON_BASE}/zjob4.png",
    "AST": f"{SDO_ICON_BASE}/zjob5.png",
    "SCH": f"{SDO_ICON_BASE}/zjob6.png",
    "SGE": f"{SDO_ICON_BASE}/zjob7.png",
    # 近战 DPS
    "MNK": f"{SDO_ICON_BASE}/zjob8.png",
    "DRG": f"{SDO_ICON_BASE}/zjob9.png",
    "NIN": f"{SDO_ICON_BASE}/zjob10.png",
    "SAM": f"{SDO_ICON_BASE}/zjob11.png",
    "RPR": f"{SDO_ICON_BASE}/zjob12.png",
    "VPR": f"{SDO_ICON_BASE}/DoW/VPR.png",
    # 远程物理 DPS
    "BRD": f"{SDO_ICON_BASE}/zjob13.png",
    "MCH": f"{SDO_ICON_BASE}/zjob14.png",
    "DNC": f"{SDO_ICON_BASE}/zjob15.png",
    # 魔法 DPS
    "BLM": f"{SDO_ICON_BASE}/zjob16.png",
    "SMN": f"{SDO_ICON_BASE}/zjob17.png",
    "RDM": f"{SDO_ICON_BASE}/zjob18.png",
    "BLU": f"{SDO_ICON_BASE}/zjob19.png",
    "PCT": f"{SDO_ICON_BASE}/DoM/PCT.png",
}

# 职业到职能的映射
JOB_ROLE = {
    "PLD": "Tank", "WAR": "Tank", "DRK": "Tank", "GNB": "Tank",
    "WHM": "Healer", "SCH": "Healer", "AST": "Healer", "SGE": "Healer",
    "MNK": "DPS", "DRG": "DPS", "NIN": "DPS", "SAM": "DPS", "RPR": "DPS", "VPR": "DPS",
    "BRD": "DPS", "MCH": "DPS", "DNC": "DPS",
    "BLM": "DPS", "SMN": "DPS", "RDM": "DPS", "BLU": "DPS", "PCT": "DPS",
}

# FFXIV 字体 URL
FFXIV_FONT_URL = "https://img.finalfantasyxiv.com/lds/pc/global/fonts/FFXIV_Lodestone_SSF.woff"


def format_time_left(seconds: float) -> str:
    if seconds <= 0:
        return "已过期"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}时{minutes}分"
    return f"{minutes}分钟"


def _role_icon(role: str, ffxiv: bool = False) -> str:
    icons = ROLE_ICONS_FFXIV if ffxiv else ROLE_ICONS_TEXT
    return icons.get(role, "?")


def _progress_bar(filled: int, total: int, width: int = 8) -> str:
    filled_blocks = min(filled, width)
    return "█" * filled_blocks + "░" * (width - filled_blocks)


def format_slot(slot: dict) -> str:
    if slot.get("filled"):
        job = slot.get("job", "?")
        role = slot.get("role", "?")
        icon = _role_icon(role)
        return f"{icon}{job}"
    else:
        role = slot.get("role")
        if role:
            return f"{_role_icon(role)}待补"
        return "？待补"


def format_listing_summary(listing: dict, index: int) -> str:
    name = listing.get("name", "未知")
    duty = listing.get("duty", "无")
    category = listing.get("category", "None")
    category_cn = CATEGORY_NAMES.get(category, category)
    dc = listing.get("datacenter", "?")
    world = listing.get("created_world", "?")
    filled = listing.get("slots_filled", 0)
    available = listing.get("slots_available", 0)
    time_left = listing.get("time_left", 0)
    desc = listing.get("description", "").strip()
    listing_id = listing.get("id", 0)
    cross = "⇔跨服" if listing.get("is_cross_world") else ""

    bar = _progress_bar(filled, available)
    time_str = format_time_left(time_left)

    lines = [
        f"#{index} {name} ({world})",
        f"  {category_cn} ─ {duty}",
        f"  {bar} {filled}/{available} │ {time_str}",
    ]
    if cross:
        lines.append(f"  {cross}")
    if desc:
        if len(desc) > 50:
            desc = desc[:47] + "..."
        lines.append(f"  「{desc}」")
    lines.append(f"  └ {dc} │ ID:{listing_id}")
    return "\n".join(lines)


def format_listing_detail(listing: dict) -> str:
    name = listing.get("name", "未知")
    duty = listing.get("duty", "无")
    category = listing.get("category", "None")
    category_cn = CATEGORY_NAMES.get(category, category)
    dc = listing.get("datacenter", "?")
    world = listing.get("created_world", "?")
    home_world = listing.get("home_world", "?")
    filled = listing.get("slots_filled", 0)
    available = listing.get("slots_available", 0)
    time_left = listing.get("time_left", 0)
    desc = listing.get("description", "").strip()
    listing_id = listing.get("id", 0)
    cross = "⇔" if listing.get("is_cross_world") else ""
    welcome = "✔" if listing.get("beginners_welcome") else "✘"
    min_il = listing.get("min_item_level", 0)
    duty_type_raw = listing.get("duty_type", "")
    duty_type = DUTY_TYPE_NAMES.get(duty_type_raw, duty_type_raw)
    objective_raw = listing.get("objective", "NONE")
    objective = OBJECTIVE_NAMES.get(objective_raw, objective_raw)
    conditions_raw = listing.get("conditions", "NONE")
    conditions = CONDITIONS_NAMES.get(conditions_raw, conditions_raw)
    loot_raw = listing.get("loot_rules", "NONE")
    loot = LOOT_NAMES.get(loot_raw, loot_raw)

    bar = _progress_bar(filled, available)

    lines = [
        f"{'─' * 28}",
        f"  {name}",
        f"{'─' * 28}",
        f"  {category_cn} │ {duty_type}",
        f"  {duty}",
        f"",
        f"  {dc} / {world} ({home_world})",
        f"  跨服: {cross or '否'} │ 新人: {welcome}",
        f"  装等: {min_il if min_il > 0 else '无要求'}",
        f"",
        f"  {bar} {filled}/{available} │ {format_time_left(time_left)}",
    ]

    if objective and objective_raw != "NONE":
        lines.append(f"  目标: {objective}")
    if conditions and conditions_raw != "NONE":
        lines.append(f"  条件: {conditions}")
    if loot and loot_raw != "NONE":
        lines.append(f"  分配: {loot}")

    slots = listing.get("slots", [])
    if slots:
        lines.append("")
        lines.append(f"{'─' * 28}")
        lines.append("  队伍槽位")
        lines.append(f"{'─' * 28}")
        for i, slot in enumerate(slots, 1):
            lines.append(f"  {i}. {format_slot(slot)}")

    if desc:
        lines.append("")
        lines.append(f"{'─' * 28}")
        lines.append("  描述")
        lines.append(f"{'─' * 28}")
        lines.append(f"  「{desc}」")

    lines.append("")
    lines.append(f"  ID: {listing_id}")
    return "\n".join(lines)


def format_listing_detail_image(listing: dict) -> str:
    name = listing.get("name", "未知")
    duty = listing.get("duty", "无")
    category = listing.get("category", "None")
    category_cn = CATEGORY_NAMES.get(category, category)
    dc = listing.get("datacenter", "?")
    world = listing.get("created_world", "?")
    filled = listing.get("slots_filled", 0)
    available = listing.get("slots_available", 0)
    time_left = listing.get("time_left", 0)
    desc = listing.get("description", "").strip()
    cross = "⇔" if listing.get("is_cross_world") else ""
    welcome = "✔" if listing.get("beginners_welcome") else "✘"
    min_il = listing.get("min_item_level", 0)
    duty_type_raw = listing.get("duty_type", "")
    duty_type = DUTY_TYPE_NAMES.get(duty_type_raw, duty_type_raw)
    listing_id = listing.get("id", 0)
    time_str = format_time_left(time_left)

    slots = listing.get("slots", [])
    slot_html = ""
    for i, slot in enumerate(slots, 1):
        filled_slot = slot.get("filled")
        role = slot.get("role")
        job_str = slot.get("job", "")
        first_job = job_str.split()[0] if job_str else ""

        role_color = ROLE_COLORS.get(role, "#888")
        role_icon = ROLE_ICONS_FFXIV.get(role, "?")
        role_cn = ROLE_CN.get(role, "任意")

        if filled_slot and first_job:
            job_icon_url = JOB_ICON_URLS.get(first_job, "")
            job_img = f'<img src="{job_icon_url}" width="28" height="28" style="border-radius:4px;" />' if job_icon_url else f'<span style="font-size:11px;color:#aaa;">{first_job}</span>'
            slot_html += f'''<div style="display:flex;align-items:center;gap:8px;padding:6px 10px;background:rgba(255,255,255,0.05);border-radius:6px;border-left:3px solid {role_color};">
  <span style="font-family:FFXIV,sans-serif;font-size:16px;">{role_icon}</span>
  {job_img}
  <span style="font-size:12px;color:#ccc;">{first_job}</span>
  <span style="margin-left:auto;font-size:10px;color:{role_color};">●</span>
</div>\n'''
        else:
            slot_html += f'''<div style="display:flex;align-items:center;gap:8px;padding:6px 10px;background:rgba(255,255,255,0.03);border-radius:6px;border-left:3px solid #555;opacity:0.7;">
  <span style="font-family:FFXIV,sans-serif;font-size:16px;">{role_icon if role else "?"}</span>
  <span style="font-size:12px;color:#888;">{role_cn if role else "任意"}</span>
  <span style="margin-left:auto;font-size:10px;color:#555;">○</span>
</div>\n'''

    tags_html = ""
    if cross:
        tags_html += f'<span style="background:#2d4a7a;padding:2px 8px;border-radius:4px;font-size:11px;">{cross}</span>'
    tags_html += f'<span style="background:#2d4a7a;padding:2px 8px;border-radius:4px;font-size:11px;">新人:{welcome}</span>'
    if min_il > 0:
        tags_html += f'<span style="background:#2d4a7a;padding:2px 8px;border-radius:4px;font-size:11px;">装等≥{min_il}</span>'

    desc_html = f'<div style="margin-top:12px;padding:10px;background:rgba(255,255,255,0.03);border-radius:6px;font-size:12px;color:#aaa;">「{desc}」</div>' if desc else ""

    return f'''<div style="font-family:'Microsoft YaHei','Segoe UI',sans-serif;padding:0;width:480px;background:#0d1117;color:#e6edf3;border-radius:12px;overflow:hidden;">
  <!-- Header -->
  <div style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);padding:16px 20px;border-bottom:2px solid #3d85c6;">
    <div style="font-size:18px;font-weight:bold;color:#fff;margin-bottom:4px;">{name}</div>
    <div style="font-size:12px;color:#8b949e;">{category_cn} │ {duty_type} │ {dc} ─ {world}</div>
  </div>

  <!-- Duty & Stats -->
  <div style="padding:16px 20px;">
    <div style="display:flex;gap:12px;margin-bottom:14px;">
      <div style="flex:1;background:#161b22;padding:10px 12px;border-radius:8px;border:1px solid #30363d;">
        <div style="font-size:10px;color:#8b949e;text-transform:uppercase;">副本</div>
        <div style="font-size:15px;font-weight:600;color:#f0f6fc;margin-top:2px;">{duty}</div>
      </div>
      <div style="flex:0.6;background:#161b22;padding:10px 12px;border-radius:8px;border:1px solid #30363d;">
        <div style="font-size:10px;color:#8b949e;text-transform:uppercase;">进度</div>
        <div style="font-size:15px;font-weight:600;color:#f0f6fc;margin-top:2px;">{filled}/{available}</div>
      </div>
      <div style="flex:0.6;background:#161b22;padding:10px 12px;border-radius:8px;border:1px solid #30363d;">
        <div style="font-size:10px;color:#8b949e;text-transform:uppercase;">剩余</div>
        <div style="font-size:15px;font-weight:600;color:#f0f6fc;margin-top:2px;">{time_str}</div>
      </div>
    </div>

    <!-- Tags -->
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px;">
      {tags_html}
    </div>

    <!-- Slots -->
    <div style="margin-bottom:4px;font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:1px;">队伍槽位</div>
    <div style="display:flex;flex-direction:column;gap:4px;">
      {slot_html}
    </div>

    {desc_html}
  </div>

  <!-- Footer -->
  <div style="padding:8px 20px;background:#161b22;border-top:1px solid #30363d;font-size:10px;color:#484f58;text-align:right;">
    ID: {listing_id} │ remote-party-finder
  </div>
</div>'''


class XpfPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.api_base = config.get("api_base_url", "https://xivpf.littlenightmare.top/api")
        self.default_dc = config.get("default_datacenter", "")
        self.default_per_page = min(config.get("default_per_page", 5), 100)
        self.as_image = config.get("result_as_image", False)

    async def _fetch_listings(self, params: dict) -> dict:
        clean = {k: v for k, v in params.items() if v is not None and v != ""}
        async with aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session:
            async with session.get(f"{self.api_base}/listings", params=clean, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(f"API 返回 {resp.status}: {text[:200]}")
                return await resp.json()

    async def _fetch_detail(self, listing_id: int) -> dict:
        async with aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session:
            async with session.get(f"{self.api_base}/listing/{listing_id}", timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 404:
                    raise ValueError("未找到该招募信息（可能已过期或被移除）")
                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(f"API 返回 {resp.status}: {text[:200]}")
                return await resp.json()

    # ── 指令组 ──

    @event_filter.command_group("pf")
    def pf(self):
        '''FFXIV 集招募查询指令组'''
        pass

    # ── /pf help ──

    @pf.command("help")
    async def pf_help(self, event: AstrMessageEvent):
        '''显示帮助信息'''
        dc_list = "、".join(DATACENTER_WORLDS.keys())
        cat_list = "、".join(CATEGORY_NAMES.values())
        yield event.plain_result(
            "FFXIV 集招募查询\n"
            "\n"
            "/pf list [大区] [页码] - 查看最新招募\n"
            "/pf search <关键词> [页码] - 搜索招募\n"
            "/pf dc <大区> [页码] - 按大区筛选\n"
            "/pf duty <副本ID> [页码] - 按副本筛选\n"
            "/pf cat <类别> [页码] - 按类别筛选\n"
            "/pf detail <ID> - 查看招募详情\n"
            "/pf help - 显示帮助\n"
            "\n"
            f"可用大区: {dc_list}\n"
            f"可用类别: {cat_list}\n"
            "示例: /pf list 豆豆柴\n"
            "示例: /pf search 绝\n"
            "示例: /pf cat 高难度任务"
        )

    # ── /pf list [大区] [页码] ──

    @pf.command("list")
    async def pf_list(self, event: AstrMessageEvent, datacenter: str = "", page: int = 1):
        '''查看最新招募 /pf list [大区] [页码]'''
        dc = datacenter or self.default_dc
        try:
            params = {"per_page": self.default_per_page, "page": max(page, 1)}
            if dc:
                params["datacenter"] = dc
            data = await self._fetch_listings(params)
            listings = data.get("data", [])
            pagination = data.get("pagination", {})

            if not listings:
                dc_hint = f"（{dc}）" if dc else ""
                yield event.plain_result(f"暂无招募信息{dc_hint}")
                return

            header = "最新招募" + (f" [{dc}]" if dc else "") + f" ({pagination.get('total', '?')}条)\n"
            body = "\n\n".join(
                format_listing_summary(l, i + 1) for i, l in enumerate(listings)
            )
            footer = f"\n---\n第 {pagination.get('page', 1)}/{pagination.get('total_pages', 1)} 页"

            if self.as_image:
                yield event.image_result(await self.text_to_image(header + body + footer))
            else:
                yield event.plain_result(header + body + footer)

        except Exception as e:
            logger.error(f"pf list error: {e}")
            yield event.plain_result(f"查询失败: {e}")

    # ── /pf search <关键词> [页码] ──

    @pf.command("search")
    async def pf_search(self, event: AstrMessageEvent, keyword: str, page: int = 1):
        '''搜索招募 /pf search <关键词> [页码]'''
        try:
            params = {
                "search": keyword,
                "per_page": self.default_per_page,
                "page": max(page, 1),
            }
            data = await self._fetch_listings(params)
            listings = data.get("data", [])
            pagination = data.get("pagination", {})

            if not listings:
                yield event.plain_result(f"未找到与 \"{keyword}\" 相关的招募")
                return

            header = f"搜索 \"{keyword}\" 的结果 ({pagination.get('total', '?')}条)\n"
            body = "\n\n".join(
                format_listing_summary(l, i + 1) for i, l in enumerate(listings)
            )
            footer = f"\n---\n第 {pagination.get('page', 1)}/{pagination.get('total_pages', 1)} 页"

            if self.as_image:
                yield event.image_result(await self.text_to_image(header + body + footer))
            else:
                yield event.plain_result(header + body + footer)

        except Exception as e:
            logger.error(f"pf search error: {e}")
            yield event.plain_result(f"查询失败: {e}")

    # ── /pf dc <大区> [页码] ──

    @pf.command("dc")
    async def pf_dc(self, event: AstrMessageEvent, datacenter: str, page: int = 1):
        '''按大区筛选 /pf dc <大区> [页码]'''
        try:
            params = {
                "datacenter": datacenter,
                "per_page": self.default_per_page,
                "page": max(page, 1),
            }
            data = await self._fetch_listings(params)
            listings = data.get("data", [])
            pagination = data.get("pagination", {})

            if not listings:
                servers = DATACENTER_WORLDS.get(datacenter, [])
                hint = f"，该大区包含: {'、'.join(servers)}" if servers else ""
                yield event.plain_result(f"大区 \"{datacenter}\" 暂无招募{hint}")
                return

            header = f"[{datacenter}] 最新招募 ({pagination.get('total', '?')}条)\n"
            body = "\n\n".join(
                format_listing_summary(l, i + 1) for i, l in enumerate(listings)
            )
            footer = f"\n---\n第 {pagination.get('page', 1)}/{pagination.get('total_pages', 1)} 页"

            if self.as_image:
                yield event.image_result(await self.text_to_image(header + body + footer))
            else:
                yield event.plain_result(header + body + footer)

        except Exception as e:
            logger.error(f"pf dc error: {e}")
            yield event.plain_result(f"查询失败: {e}")

    # ── /pf duty <副本ID> [页码] ──

    @pf.command("duty")
    async def pf_duty(self, event: AstrMessageEvent, duty_id: str, page: int = 1):
        '''按副本筛选 /pf duty <副本ID> [页码]（支持逗号分隔多个ID）'''
        try:
            params = {
                "duty": duty_id,
                "per_page": self.default_per_page,
                "page": max(page, 1),
            }
            data = await self._fetch_listings(params)
            listings = data.get("data", [])
            pagination = data.get("pagination", {})

            if not listings:
                yield event.plain_result(f"副本 {duty_id} 暂无招募")
                return

            header = f"副本 {duty_id} 的招募 ({pagination.get('total', '?')}条)\n"
            body = "\n\n".join(
                format_listing_summary(l, i + 1) for i, l in enumerate(listings)
            )
            footer = f"\n---\n第 {pagination.get('page', 1)}/{pagination.get('total_pages', 1)} 页"

            if self.as_image:
                yield event.image_result(await self.text_to_image(header + body + footer))
            else:
                yield event.plain_result(header + body + footer)

        except Exception as e:
            logger.error(f"pf duty error: {e}")
            yield event.plain_result(f"查询失败: {e}")

    # ── /pf cat <类别> [页码] ──

    @pf.command("cat")
    async def pf_cat(self, event: AstrMessageEvent, category: str, page: int = 1):
        '''按类别筛选 /pf cat <类别> [页码]'''
        # 支持中文类别名反查英文 key
        cat_key = category
        for eng, cn in CATEGORY_NAMES.items():
            if cn == category:
                cat_key = eng
                break

        try:
            params = {
                "category": cat_key,
                "per_page": self.default_per_page,
                "page": max(page, 1),
            }
            data = await self._fetch_listings(params)
            listings = data.get("data", [])
            pagination = data.get("pagination", {})

            if not listings:
                yield event.plain_result(f"类别 \"{category}\" 暂无招募")
                return

            cat_display = CATEGORY_NAMES.get(cat_key, cat_key)
            header = f"[{cat_display}] 最新招募 ({pagination.get('total', '?')}条)\n"
            body = "\n\n".join(
                format_listing_summary(l, i + 1) for i, l in enumerate(listings)
            )
            footer = f"\n---\n第 {pagination.get('page', 1)}/{pagination.get('total_pages', 1)} 页"

            if self.as_image:
                yield event.image_result(await self.text_to_image(header + body + footer))
            else:
                yield event.plain_result(header + body + footer)

        except Exception as e:
            logger.error(f"pf cat error: {e}")
            yield event.plain_result(f"查询失败: {e}")

    # ── /pf detail <ID> ──

    @pf.command("detail")
    async def pf_detail(self, event: AstrMessageEvent, listing_id: int):
        '''查看招募详情 /pf detail <ID>'''
        try:
            listing = await self._fetch_detail(listing_id)

            if self.as_image:
                html = format_listing_detail_image(listing)
                yield event.image_result(await self.html_render(html, {}))
            else:
                yield event.plain_result(format_listing_detail(listing))

        except ValueError as e:
            yield event.plain_result(str(e))
        except Exception as e:
            logger.error(f"pf detail error: {e}")
            yield event.plain_result(f"查询失败: {e}")

    async def terminate(self):
        pass
