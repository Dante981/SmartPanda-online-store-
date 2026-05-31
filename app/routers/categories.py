from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.categories import Category as CategoryModel
from app.schemas import Category as CategorySchema, CategoryCreate
from app.db_depends import get_db, get_async_db


#Создаём маршрутизатор с префиксом и тегом
router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)

@router.get("/", response_model=list[CategorySchema], status_code=status.HTTP_200_OK)
async def get_all_categories(db: AsyncSession = Depends(get_async_db)) -> list[CategorySchema]:
    """
    Возвращает список всех категорий товаров.
    """
    stmt = select(CategoryModel).where(CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    categories = result.all()
    return categories

@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_async_db)) -> CategorySchema:
    """
    Создаёт новую категорию
    """
    if category.parent_id is not None:
        stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id,
                                           CategoryModel.is_active == True)
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    return db_category




@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(category_id: int, category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет категорию по её ID.
    """
    # Проверка существования категории
    stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                       CategoryModel.is_active == True)
    result_category = await db.scalars(stmt)
    db_category = result_category.first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Проверка существования parent_id, если указан
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id,
                                                  CategoryModel.is_active == True)
        result_parent = await db.scalars(parent_stmt)
        parent = result_parent.first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")
    
    # Обновление категории
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category.model_dump())
    )
    await db.commit()
    return db_category




@router.delete("/{category_id}", status_code=status.HTTP_200_OK, response_model=CategorySchema)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db)) -> CategorySchema:
    """
    Удаляет категорию по её ID.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    await db.execute(update(CategoryModel).where(CategoryModel.id == category_id).values(is_active=False))
    await db.commit()
    await db.refresh(category)
    return category