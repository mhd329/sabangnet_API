from schemas.product.modified_product_dto import ModifiedProductDataDto
from schemas.product.product_raw_data_dto import ProductRawDataDto
from schemas.product.response.product_response import ProductNameResponse
from repository.product_repository import ProductRepository
from sqlalchemy.ext.asyncio import AsyncSession

class ProductWriteService:
    def __init__(self, session: AsyncSession) -> None:
        self.product_repository = ProductRepository(session)

    async def modify_product_name(self, compayny_goods_cd: str, product_name: str) -> ModifiedProductDataDto:
        
        product_raw_data = await self.product_repository.find_product_raw_data_by_company_goods_cd(compayny_goods_cd)
        if product_raw_data is None:
            raise ValueError(f"Product raw data not found: {compayny_goods_cd}")
        
        modified_product_data = await self.product_repository.\
            find_modified_product_data_by_product_raw_data_id(product_raw_data.id)
        
        rev = 0 if modified_product_data is None else modified_product_data.rev + 1
        
        result = await self.product_repository.save_modified_product_name(
            product_raw_data=product_raw_data, rev=rev, product_name=product_name)
        
        dto = ModifiedProductDataDto.model_validate(result)
        return dto
    
    async def get_products(self, page: int) -> list[ProductRawDataDto]:
        products = await self.product_repository.get_products(page=page)
        dtos = [ProductRawDataDto.model_validate(product) for product in products]
        return dtos
    