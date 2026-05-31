from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db_depends import get_db, get_async_db
from app.models import Product as ProductModel, Category as CategoryModel
from app.schemas import Product as ProductSchema, ProductCreate

# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)) -> list[ProductSchema]:
    """
    Возвращает список всех товаров.
    """
    stmt = select(ProductModel).where(ProductModel.is_active == True)
    result = await db.scalars(stmt)
    products = result.all()

    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_async_db)) -> ProductSchema:
    """
    Создаёт новый товар.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id,
                                        CategoryModel.is_active == True)
    result_category = await db.scalars(stmt)
    db_category = result_category.first()
    if db_category is None:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema])
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)) -> list[ProductSchema]:
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                       CategoryModel.is_active == True)
    result_category = await db.scalars(stmt)
    db_category = result_category.first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found or inactive")

    stmt = select(ProductModel).where(ProductModel.category_id == category_id,
                                      ProductModel.is_active == True)
    result_products = await db.scalars(stmt)
    products_by_category = result_products.all()

    return products_by_category


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)) -> ProductSchema:
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    

    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active == True)
    result_product = await db.scalars(stmt)
    db_product = result_product.first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    
    stmt = select(CategoryModel).where(CategoryModel.id == db_product.category_id,
                                       CategoryModel.is_active == True)
    result_category = await db.scalars(stmt)
    db_category = result_category.first()
    if db_category is None:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    return db_product


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, new_product: ProductCreate, db: AsyncSession = Depends(get_async_db)) -> ProductSchema:
    """
    Обновляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active == True)
    result_product = await db.scalars(stmt)
    db_product = result_product.first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    stmt = select(CategoryModel).where(CategoryModel.id == new_product.category_id,
                                       CategoryModel.is_active == True)
    result_category = await db.scalars(stmt)
    db_category = result_category.first()
    if db_category is None:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    
    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id,)
        .values(**new_product.model_dump()))
    await db.commit()
    await db.refresh(db_product)

    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductSchema)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_async_db)) -> ProductSchema:
    """
    Удаляет товар по его ID.
    """

    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                       ProductModel.is_active == True)
    result_product = await db.scalars(stmt)
    db_product = result_product.first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active=False))
    await db.commit()
    await db.refresh(db_product)

    return db_product
