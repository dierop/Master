import pandas as pd
from difflib import get_close_matches

class DataHandler():
    data: pd.DataFrame
    supermarket: str = None

    def __init__(self, path="productos-de-supermercado-sample.csv"):
        self.data = pd.read_csv(path)
        self.data["name"] = self.data["name"].str.lower()
        self.data.drop(columns=["reference_price","insert_date", "reference_unit", "description"], inplace=True, axis=1)

        self.data.drop_duplicates(inplace=True)

    def set_supermarket(self, supermarket: str):
        s= self.data["supermarket"].unique()
        for i in s:
            for j in supermarket.split():
                if j in i:
                    self.supermarket = i
                    return True
        return False

    def get_supermarkets(self):
        return self.data["supermarket"].unique().tolist()


    def get_random_product(self):
        products = self.data[self.data["supermarket"]==self.supermarket]
        return products.sample().loc[:, ["name", "price"]].to_dict(orient='records')[0]
    
    def get_by_price(self, price: float):
        return self.data[(self.data["supermarket"]==self.supermarket) & (self.data["price"]<=price)].to_dict(orient='records')
    
    def get_by_category(self, category: str):
        return self.data[(self.data["supermarket"]==self.supermarket) & (self.data["category"]==category)].to_dict(orient='records')

    def get_by_name(self, name: str, type: str="name"):
        result = self.data[(self.data[type]==name) & (self.data["supermarket"]==self.supermarket)].to_dict(orient='records')#[0]
        if len(result) == 0:
            suggestions = get_close_matches(name, self.data[self.data["supermarket"]==self.supermarket][type].tolist(), n=3, cutoff=0.9)
            if len(suggestions) > 0:
                return self.get_by_name(suggestions[0], type)
            return None
        return result
    def get_similar(self, name: str, type: str="name"):
        product_names = self.data[(self.data["supermarket"]==self.supermarket) & (self.data[type].str.contains(name))][type].tolist()[:3]
        
        suggestions = get_close_matches(name, self.data[self.data["supermarket"]==self.supermarket][type].tolist(), n=3, cutoff=0.6)

        return list(set(product_names + suggestions))
    
    def get_categories(self):
        return self.data["category"].unique().tolist()
    
    def get_by_price_category(self, price: float):
        return self.data[(self.data["supermarket"]==self.supermarket) & (self.data["price"]<=price)].to_dict(orient='records')