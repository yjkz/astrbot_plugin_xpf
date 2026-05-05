import aiohttp
from astrbot.api.event import filter, AstrMessageEvent
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
}

# 大区到服务器的映射（国服）
DATACENTER_WORLDS = {
    "莫古力": ["潮风亭", "神拳痕", "白银乡", "白金幻象", "红茶川"],
    "猫小胖": ["紫水栈桥", "延夏", "静语庄园", "摩杜纳", "海猫茶屋"],
    "豆豆柴": ["水晶塔", "银泪湖", "伊修加德", "太阳海岸", "亚马乌罗提"],
    "陆行鸟": ["红玉海", "神意之地", "拉诺西亚", "幻影群岛", "萌芽池"],
}


def format_time_left(seconds: float) -> str:
    if seconds <= 0:
        return "已过期"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}时{minutes}分"
    return f"{minutes}分钟"


def format_slot(slot: dict) -> str:
    if slot.get("filled"):
        job = slot.get("job", "?")
        role = slot.get("role", "?")
        return f"[{role}] {job}"
    else:
        role = slot.get("role")
        if role:
            return f"[{role}] 待补"
        return "[任意] 待补"


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
    cross = "跨服" if listing.get("is_cross_world") else ""

    tags = " ".join(filter(None, [cross]))

    lines = [
        f"#{index} | {name} ({world})",
        f"  {category_cn} - {duty}",
        f"  {filled}/{available}人 | 剩余{format_time_left(time_left)}",
    ]
    if tags:
        lines.append(f"  {tags}")
    if desc:
        if len(desc) > 60:
            desc = desc[:57] + "..."
        lines.append(f"  {desc}")
    lines.append(f"  ID: {listing_id}  |  {dc}")
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
    cross = "是" if listing.get("is_cross_world") else "否"
    welcome = "是" if listing.get("beginners_welcome") else "否"
    min_il = listing.get("min_item_level", 0)
    duty_type = listing.get("duty_type", "")
    objective = listing.get("objective", "NONE")
    conditions = listing.get("conditions", "NONE")
    loot = listing.get("loot_rules", "NONE")

    lines = [
        f"{name} 的招募",
        "",
        "【信息】",
        f"副本: {duty}",
        f"类别: {category_cn}",
        f"类型: {duty_type}",
        f"大区: {dc} / {world}",
        f"属服: {home_world}",
        f"跨服: {cross}",
        f"新人欢迎: {welcome}",
        f"最低装等: {min_il if min_il > 0 else '无要求'}",
        "",
        "【招募状态】",
        f"已满: {filled}/{available} 人",
        f"剩余时间: {format_time_left(time_left)}",
    ]

    if objective and objective != "NONE":
        lines.append(f"目标: {objective}")
    if conditions and conditions != "NONE":
        lines.append(f"条件: {conditions}")
    if loot and loot != "NONE":
        lines.append(f"分配: {loot}")

    slots = listing.get("slots", [])
    if slots:
        lines.append("")
        lines.append("【队伍槽位】")
        for i, slot in enumerate(slots, 1):
            lines.append(f"  {i}. {format_slot(slot)}")

    if desc:
        lines.append("")
        lines.append("【描述】")
        lines.append(f"  {desc}")

    lines.append("")
    lines.append(f"ID: {listing_id}")
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
    cross = "✔" if listing.get("is_cross_world") else "✘"
    welcome = "✔" if listing.get("beginners_welcome") else "✘"
    min_il = listing.get("min_item_level", 0)
    duty_type = listing.get("duty_type", "")

    slots = listing.get("slots", [])
    slot_rows = ""
    for i, slot in enumerate(slots, 1):
        if slot.get("filled"):
            role = slot.get("role", "?")
            job = slot.get("job", "?")
            slot_rows += f'<tr class="filled"><td>{i}</td><td>{role}</td><td>{job}</td><td>✅</td></tr>\n'
        else:
            role = slot.get("role") or "任意"
            slot_rows += f'<tr class="empty"><td>{i}</td><td>{role}</td><td>-</td><td>❓</td></tr>\n'

    return f'''
<div style="font-family: 'Microsoft YaHei', sans-serif; padding: 20px; width: 500px; background: #1a1a2e; color: #eee; border-radius: 12px;">
  <h2 style="color: #e94560; margin: 0 0 8px 0;">{name}</h2>
  <div style="color: #888; font-size: 13px; margin-bottom: 16px;">{category_cn} | {duty_type} | {dc} - {world}</div>

  <div style="display: flex; gap: 16px; margin-bottom: 16px;">
    <div style="flex:1; background: #16213e; padding: 12px; border-radius: 8px;">
      <div style="font-size: 12px; color: #888;">副本</div>
      <div style="font-size: 16px; font-weight: bold;">{duty}</div>
    </div>
    <div style="flex:1; background: #16213e; padding: 12px; border-radius: 8px;">
      <div style="font-size: 12px; color: #888;">进度</div>
      <div style="font-size: 16px; font-weight: bold;">{filled}/{available} 人</div>
    </div>
    <div style="flex:1; background: #16213e; padding: 12px; border-radius: 8px;">
      <div style="font-size: 12px; color: #888;">剩余</div>
      <div style="font-size: 16px; font-weight: bold;">{format_time_left(time_left)}</div>
    </div>
  </div>

  <div style="display: flex; gap: 12px; margin-bottom: 16px; font-size: 13px;">
    <span>跨服: {cross}</span>
    <span>新人欢迎: {welcome}</span>
    <span>装等要求: {min_il if min_il > 0 else "无"}</span>
  </div>

  <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
    <thead>
      <tr style="background: #0f3460;">
        <th style="padding: 8px; text-align: left;">#</th>
        <th style="padding: 8px; text-align: left;">职能</th>
        <th style="padding: 8px; text-align: left;">职业</th>
        <th style="padding: 8px; text-align: left;">状态</th>
      </tr>
    </thead>
    <tbody>
      {slot_rows}
    </tbody>
  </table>

  {"<div style='background: #16213e; padding: 12px; border-radius: 8px; font-size: 13px;'><b>描述:</b> " + desc + "</div>" if desc else ""}
</div>
'''


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

    @filter.command_group("pf")
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
