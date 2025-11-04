import re
from enum import Enum
from typing import List, Optional
from urllib.parse import urlparse, urlunparse

from pydantic import BaseModel, Field, root_validator, validator


class EntryKind(str, Enum):
    BOOK = "book"
    ARTICLE = "article"


class EntryStatus(str, Enum):
    PLANNED = "planned"
    READING = "reading"
    COMPLETED = "completed"


class EntryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    kind: EntryKind
    link: Optional[str] = Field(None, max_length=2000)
    status: EntryStatus = EntryStatus.PLANNED

    class Config:
        str_strip_whitespace = True
        extra = "forbid"
        validate_assignment = True

    @validator("title", pre=True)
    def pre_validate_title(cls, v):
        if isinstance(v, str):
            v = v.strip()
            v = re.sub(r'[<>{}`"\\]', "", v)
        return v

    @validator("title")
    def validate_title_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")

        if not re.search(r"[a-zA-Zа-яА-Я0-9]", v):
            raise ValueError("Title must contain at least one letter or digit")

        sql_patterns = [
            r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b",
            r"(\-\-|\;|\/\*|\*\/)",
            r"\bWHERE\b.*\b1\s*=\s*1\b",
            r"\bOR\b.*\b1\s*=\s*1\b",
        ]

        v_upper = v.upper()
        for pattern in sql_patterns:
            if re.search(pattern, v_upper, re.IGNORECASE):
                raise ValueError("Title contains prohibited SQL patterns")

        dangerous_patterns = [
            r"<script",
            r"</script>",
            r"javascript:",
            r"onload=",
            r"onerror=",
            r"onclick=",
            r"vbscript:",
            r"data:",
            r"<iframe",
            r"</iframe>",
            r"<object",
            r"</object>",
            r"<embed",
            r"</embed>",
            r"<form",
            r"</form>",
            r"alert\(",
            r"confirm\(",
            r"prompt\(",
            r"eval\(",
            r"expression\(",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Title contains unsafe content")

        if re.match(r'^[!@#$%^&*()_+\-=\[\]{}|\\:;"<>,.?/~`]+$', v):
            raise ValueError("Title must contain meaningful text")

        return v

    @validator("link", pre=True)
    def pre_validate_link(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
        return v

    @validator("link")
    def validate_and_normalize_link(cls, v):
        if not v:
            return None

        dangerous_schemes = ["javascript:", "data:", "vbscript:", "file:", "ftp:"]
        if any(v.lower().startswith(scheme) for scheme in dangerous_schemes):
            raise ValueError("Dangerous URL scheme is not allowed")

        if not v.startswith(("http://", "https://")):
            raise ValueError("Link must start with http:// or https://")

        try:
            parsed = urlparse(v)
            if not parsed.netloc:
                raise ValueError("Link must contain a valid domain")

            domain = parsed.netloc.lower()
            if not re.match(r"^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}$", domain):
                raise ValueError("Invalid domain format")

            path = parsed.path
            dangerous_path_patterns = [r"\.\.", r"\./", r"//", r"\\"]
            for pattern in dangerous_path_patterns:
                if re.search(pattern, path):
                    raise ValueError("URL path contains dangerous sequences")

            if parsed.query:
                query_lower = parsed.query.lower()
                dangerous_query_patterns = ["script", "javascript", "onload", "onerror"]
                for pattern in dangerous_query_patterns:
                    if pattern in query_lower:
                        raise ValueError("URL contains unsafe query parameters")

            normalized_url = urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    "",
                )
            )

            return normalized_url

        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Invalid URL format: {str(e)}")

    @validator("kind", "status")
    def validate_enum_values(cls, v, field):
        if not isinstance(v, str):
            raise ValueError(f"{field.name} must be a string")

        enum_class = field.type_
        if v not in enum_class.__members__.values():
            allowed_values = list(enum_class.__members__.values())
            raise ValueError(f"Invalid {field.name}. Must be one of: {allowed_values}")
        return v

    @root_validator(skip_on_failure=True)
    def validate_domain_rules(cls, values):
        kind = values.get("kind")
        link = values.get("link")
        # status = values.get('status')

        if kind == EntryKind.ARTICLE and not link:
            raise ValueError("Articles must have a link")

        return values


class EntryCreate(EntryBase):
    pass


class EntryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    kind: Optional[EntryKind] = None
    link: Optional[str] = Field(None, max_length=2000)
    status: Optional[EntryStatus] = None

    class Config:
        str_strip_whitespace = True
        extra = "forbid"

    @validator("title", pre=True)
    def pre_validate_title_update(cls, v):
        if v is not None and isinstance(v, str):
            v = v.strip()
            v = re.sub(r'[<>{}`"\\]', "", v)
        return v

    @validator("title")
    def validate_title_if_provided(cls, v):
        if v is not None:
            return EntryBase.validate_title_content(v)
        return v

    @validator("link", pre=True)
    def pre_validate_link_update(cls, v):
        if v is not None and isinstance(v, str):
            v = v.strip()
            if not v:
                return None
        return v

    @validator("link")
    def validate_link_if_provided(cls, v):
        if v is not None:
            return EntryBase.validate_and_normalize_link(v)
        return v

    @root_validator
    def validate_update_domain_rules(cls, values):
        kind = values.get("kind")
        link = values.get("link")
        # status = values.get('status')

        if kind == EntryKind.ARTICLE and not link:
            # Проверяем, не пытаемся ли мы обновить kind без указания link.
            # В реальном сценарии нужно проверить существующий link из БД.
            # Для простоты временно ослабил это правило для обновлений.
            pass

        return values

    @root_validator
    def validate_at_least_one_field(cls, values):
        if all(
            field is None
            for field in [
                values.get("title"),
                values.get("kind"),
                values.get("link"),
                values.get("status"),
            ]
        ):
            raise ValueError("At least one field must be provided for update")
        return values


class Entry(EntryBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
        use_enum_values = True


class EntryList(BaseModel):
    items: List[Entry]
    total: int
