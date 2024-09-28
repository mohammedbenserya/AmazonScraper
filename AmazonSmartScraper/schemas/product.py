from pydantic import BaseModel, Field
from typing import List, Optional
import datetime
class Product(BaseModel):
    """
    Represents a product with various attributes scraped from Amazon.
    """

    asin: str = Field(max_length=120, unique=True, db_index=True)
    url: Optional[str] = Field(default=None,blank=True, null=True)
    title: Optional[str] = Field(default=None,max_length=220, blank=True, null=True)
    image: Optional[str] = Field(default=None,blank=True, null=True)
    description: Optional[str] = Field(default=None,blank=True, null=True)
    price_raw: Optional[str] = Field(default=None,blank=True, null=True)
    price_text: Optional[str] = Field(default=None,blank=True, null=True)
    price: Optional[float] = Field(blank=True, null=True, default=0.00)
    currency: Optional[str] = Field(default=None,blank=True, null=True)
    rating: Optional[str] = Field(default=None,blank=True, null=True)
    brand: Optional[str] = Field(default=None,blank=True, null=True)
    nbr_rating: Optional[str] = Field(default=None,blank=True, null=True)
    is_out_of_stock: Optional[bool] = Field(default=None,blank=True, null=True)
    alias: Optional[str] = Field(default=None,max_length=220, blank=True, null=True)
    keyword: Optional[str] = Field(default=None,max_length=220, blank=True, null=True)
    page: Optional[int] = Field(blank=True, null=True, default=1)
    metadata: Optional[List[dict]] = Field(default=None,blank=True, null=True)
    timestamp: Optional[datetime.datetime] = Field(auto_now_add=True, default=datetime.datetime.now())
    # updated: Optional[datetime.datetime] = Field(auto_now=True)

    class Config:
        """
        Configuration for the Product model.
        """
        from_attributes = True
        json_schema_extra = {
            "example": {
                "asin": "B0B1M6ML2J",
                "url": "https://www.amazon.com/dp/B0B1M6ML2J",
                "title": "Apple iPhone 13 Pro Max",
                "image": "https://m.media-amazon.com/images/I/71DVgBTdyLL._AC_SL1500_.jpg",
                "description": "The iPhone 13 Pro Max is the best iPhone ever.",
                "price_raw": "$1,099.00",
                "price_text": "1099.00",
                "price": 1099.00,
                "currency": "$",
                "rating": "4.5 out of 5 stars",
                "brand": "Apple",
                "nbr_rating": "1,234 ratings",
                "is_out_of_stock": False,
                "metadata": [
                    {"Brand": "Apple"},
                    {"Operating System": "iOS"},
                    {"Wireless Carrier": "Unlocked"},
                    {"Color": "Graphite"},
                    {"Memory Storage Capacity": "256 GB"},
                    {"Other camera features": "Rear, Front"},
                    {"Form Factor": "Smartphone"},
                    {"Manufacturer": "Apple Computer"},
                    {"Date First Available": "September 14, 2021"}
                ],
                "alias": "phones",
                "keyword": "phones",
                "page": 1,
                "timestamp": "2022-02-22T12:00:00"
            }
        }

# class Pagination(BaseModel):
#         count: int
#         class Config:
#             from_attributes = True
#             json_schema_extra = {
#                 "example": {
#                     "count": 10
#                 }
#             }