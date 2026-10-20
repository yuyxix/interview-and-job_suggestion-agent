import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# =============================
# 岗位记录的字段清单（唯一来源：工具、筛选、入参校验都从这里取）
# =============================
JOB_FIELDS = (
    "job_id",       # 岗位ID
    "industry",     # 行业（调用方打的标签）
    "domain",       # 领域（调用方打的标签）
    "job_role",     # 岗位类别（调用方打的标签）
    "keyword",      # 命中的搜索关键词
    "job_name",     # 岗位名称
    "company",      # 公司名
    "city",         # 工作城市
    "salary",       # 薪资
    "experience",   # 经验要求
    "degree",       # 学历要求
    "job_type",     # 岗位类型（接口给的子类别，如"运维开发工程师"）
    "work_type",    # 工作性质（全职 / 兼职/临时 / 实习）
    "skills",       # 技能标签，逗号分隔，如 "Python，MySQL"
)

# 城市代码对照表 —— 只放**实测验证过**的。
# 实测结论：S_SOU_WORK_CITY 传城市名（如"成都"）不会报错，但接口会静默忽略它、
# 直接返回全国岗位。所以这里不做"城市名 → 代码"的自动映射（猜错的代码 = 悄悄给你错数据），
# 而是要求传数字代码，并且强校验是不是数字。
# 需要更多城市就自己往这里加，加完跑一次确认返回的城市对不对。
VERIFIED_CITY_CODES = {
    "全国": "489",
}


class JobSearchParams(BaseModel):

    keywords: str = Field(
        ...,
        min_length=1,
        max_length=30,
        description='岗位搜索关键词，如 python、Java开发、数据分析',
    )
    city_code: str = Field(
        "489",
        description='智联城市代码（纯数字），489=全国；必须传代码，传城市名会被接口忽略',
    )
    max_pages: int = Field(
        1,
        ge=1,
        le=5,
        description='翻多少页，每页 20 条，最多 5 页（防止一次请求太多被网站封）',
    )
    limit: int = Field(
        10,
        ge=1,
        le=30,
        description='最多返回多少条岗位；用户说“找两个”就填 2，没说数量默认 10',
    )
    # 下面这些都用"包含匹配"，所以不锁死枚举 ——
    # work_type 实际值有"全职""兼职/临时"，传"兼职"也能命中；用 Literal 反而会把自己卡死
    job_type: Optional[str] = Field(None, description='岗位类型，如 Python、C/C++、运维开发工程师')
    work_type: Optional[str] = Field(None, description='工作性质，常见值：全职、兼职/临时、实习')
    degree: Optional[str] = Field(None, description='学历要求，常见值：不限、大专、本科、硕士、博士')
    skills: Optional[str] = Field(None, description='技能要求，如 Django、MySQL')
    # 注意：这里故意没有 industry / domain / job_role。
    # 那三个是"用职位树爬取"时给每条记录打的标签，用关键词直接搜时它们恒为空字符串，
    # 拿来当筛选条件只会筛出 0 条，属于静默失效 —— 所以不暴露给智能体。
    fields: Optional[list[str]] = Field(
        None,
        description=f'只返回这些字段，不传=全部14个。可选值：{"、".join(JOB_FIELDS)}',
    )

    # ---- 参数验证 ----

    @field_validator("keywords")
    @classmethod
    def _check_keywords(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("keywords 不能全是空格")
        return v

    @field_validator("city_code")
    @classmethod
    def _check_city_code(cls, v: str) -> str:
        v = str(v).strip()
        if not re.fullmatch(r"\d+", v):
            raise ValueError(
                f"city_code 必须是数字代码，收到 {v!r}。"
                f"传城市名（如'成都'）接口不会报错但会忽略它、返回全国岗位，"
                f"所以这里直接拦掉。已验证的代码：{VERIFIED_CITY_CODES}"
            )
        return v

    @field_validator("fields")
    @classmethod
    def _check_fields(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """字段名必须是 JOB_FIELDS 里的，否则直接报错并列出合法值"""
        if v is None:
            return None
        bad = [f for f in v if f not in JOB_FIELDS]
        if bad:
            raise ValueError(f"不支持的字段 {bad}；合法字段：{list(JOB_FIELDS)}")
        return v

    @property
    def filters(self) -> dict:
        """把"有值的筛选字段"抽成 dict，直接喂给 filter_jobs"""
        return {
            k: getattr(self, k)
            for k in ("job_type", "work_type", "degree", "skills")
            if getattr(self, k)
        }


class JobParamExtraction(BaseModel):
    """岗位参数提取用的宽松 Schema

    允许 keywords 为空：用户没提方向、也没有画像时，模型应该返回空，
    由调用方提示用户补充信息，而不是为了通过校验编一个方向。
    """

    keywords: str = Field('', description='岗位关键词；无法确定时留空')
    city_code: str = Field('489', description='固定 489=全国')
    max_pages: int = Field(1, ge=1, le=5)
    limit: int = Field(10, ge=1, le=30)
    job_type: Optional[str] = None
    work_type: Optional[str] = None
    degree: Optional[str] = None
    skills: Optional[str] = None
    fields: Optional[list[str]] = None


class GetJobSchema(BaseModel):

    job_id: int = Field(..., description='招聘网站中的岗位ID，可以通过id直接检索某个岗位')
    industry: str = Field(..., description='行业，用户指定的行业标签')
    domain: str = Field(..., description='领域，用户指定的领域')
    job_role: str = Field(..., description='岗位类别，用户指定的岗位，类别')
    keyword: str = Field(..., description='命中的搜索关键词')
    job_name: str = Field(..., description='岗位名称')
    company: str = Field(..., description='公司名')
    city: str = Field(..., description='工作城市')
    salary: str = Field(..., description='薪资')
    experience: str = Field(..., description='经验要求')
    degree: str = Field(..., description='学历要求')
    job_type: str = Field(..., description='岗位类型（接口给的子类别，如"运维开发工程师"）')
    work_type: str = Field(..., description='工作性质（全职 / 兼职/临时 / 实习）')
    skills: str = Field(..., description='技能标签，逗号分隔，如 "Python，MySQL"')
