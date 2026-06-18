class ProductData:
  def __new__(self, title, description, price, brand, image_link):
    self.title = title
    self.description = description
    self.price = price
    self.brand = brand
    self.image_link = image_link

  def print_data(self) -> str:
    return f"TITLE: {self.title}\nDESCRIPTION: {self.description}\nPRICE: {self.price}\nBRAND: {self.brand}"

  title = ""
  description = ""
  price = ""
  brand = ""
  image_link = ""