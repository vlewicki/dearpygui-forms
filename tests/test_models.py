import enum
from pprint import pprint
from pydantic import BaseModel


models: list[type[BaseModel]] = []


class Category(enum.Enum):
    FOOD = "food"
    ENTERTAINMENT = "entertainment"
    TRANSPORTATION = "transportation"
    HOUSING = "housing"
    UTILITIES = "utilities"
    OTHER = 0

class Transaction(BaseModel):
    category: Category


models.append(Transaction)

class Test1(BaseModel):
    val: int | None = None

models.append(Test1)


class Test2(BaseModel):
    val: Transaction | Test1

models.append(Test2)


for model in models:
    pprint(model.model_json_schema())
    print(Test1().model_dump_json())
