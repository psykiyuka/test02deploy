from pydantic import BaseModel, field_validator


class CreateCategoryRequest(BaseModel):
    name: str
    parent_id: int | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("分类名称不能为空")
        return v.strip()


class UpdateCategoryRequest(BaseModel):
    name: str | None = None
    parent_id: int | None = None