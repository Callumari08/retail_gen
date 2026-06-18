from product_data import ProductData
import pandas as pd


def _normalise_column_name(name: str) -> str:
  return name.strip().lower().replace(" ", "_")


def gather_data(path: str) -> list[ProductData]:
  sep = "\t" if path.endswith(".tsv") else ","
  df = pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False)

  normalised_columns = {
    _normalise_column_name(column): column for column in df.columns
  }
  required_columns = ("title", "description", "price", "brand", "image_link")
  missing_columns = [
    column for column in required_columns if column not in normalised_columns
  ]
  if missing_columns:
    raise ValueError(
      f"Missing required columns: {', '.join(missing_columns)}"
    )

  products: list[ProductData] = []
  for row in df.to_dict(orient="records"):
    product = object.__new__(ProductData)
    product.title = row[normalised_columns["title"]]
    product.description = row[normalised_columns["description"]]
    product.price = row[normalised_columns["price"]]
    product.brand = row[normalised_columns["brand"]]
    product.image_link = row[normalised_columns["image_link"]]
    products.append(product)

  return products


def get_product_by_title(
  products: list[ProductData],
  title: str,
) -> ProductData | None:
  normalised_title = title.strip().casefold()

  for product in products:
    if product.title.strip().casefold() == normalised_title:
      return product

  return None
