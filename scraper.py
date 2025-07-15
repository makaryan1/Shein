import json
import random
from faker import Faker

def generate_fake_products(count=20):
    fake = Faker()
    categories = ['Clothing', 'Shoes', 'Accessories']

    products = []
    for i in range(1, count+1):
        products.append({
            "id": i,
            "name": f"{fake.word().capitalize()} {random.choice(categories)[:-1]}",
            "price": f"{random.randint(10, 200)}.{random.randint(0, 99):02d} $",
            "image": f"https://picsum.photos/300/200?random={i}",
            "category": random.choice(categories)
        })

    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    generate_fake_products()