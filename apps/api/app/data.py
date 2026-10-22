# Knowledge bases. ponytail: in-memory, move to a DB / vector store when the catalog outgrows a file.

CUSTOMER_ID = "c1"

PRODUCTS = [
    {"id": "p01", "name": "Navy wool blazer", "category": "outerwear", "price": 189, "stock": 6, "tags": ["business", "formal", "wool", "navy"]},
    {"id": "p02", "name": "White oxford shirt", "category": "top", "price": 59, "stock": 20, "tags": ["business", "classic", "cotton", "white"]},
    {"id": "p03", "name": "Charcoal tailored trousers", "category": "bottom", "price": 89, "stock": 12, "tags": ["business", "formal", "grey"]},
    {"id": "p04", "name": "Black leather loafers", "category": "shoes", "price": 129, "stock": 0, "tags": ["business", "smart casual", "leather", "black"]},
    {"id": "p05", "name": "Brown leather derby shoes", "category": "shoes", "price": 139, "stock": 8, "tags": ["business", "formal", "leather", "brown"]},
    {"id": "p06", "name": "Camel wool overcoat", "category": "outerwear", "price": 249, "stock": 4, "tags": ["business", "winter", "cold", "wool", "camel"]},
    {"id": "p07", "name": "Grey merino crewneck sweater", "category": "top", "price": 79, "stock": 15, "tags": ["smart casual", "cold", "wool", "grey"]},
    {"id": "p08", "name": "Light-blue linen shirt", "category": "top", "price": 49, "stock": 18, "tags": ["casual", "summer", "warm", "linen", "blue"]},
    {"id": "p09", "name": "Beige chinos", "category": "bottom", "price": 69, "stock": 25, "tags": ["smart casual", "cotton", "beige"]},
    {"id": "p10", "name": "Dark indigo slim jeans", "category": "bottom", "price": 79, "stock": 30, "tags": ["casual", "denim", "blue"]},
    {"id": "p11", "name": "White leather sneakers", "category": "shoes", "price": 99, "stock": 22, "tags": ["casual", "minimal", "leather", "white"]},
    {"id": "p12", "name": "Black trench coat", "category": "outerwear", "price": 199, "stock": 5, "tags": ["business", "rain", "classic", "black"]},
    {"id": "p13", "name": "Navy silk midi dress", "category": "dress", "price": 149, "stock": 7, "tags": ["business", "elegant", "silk", "navy"]},
    {"id": "p14", "name": "Cream knit cardigan", "category": "top", "price": 89, "stock": 9, "tags": ["smart casual", "cold", "knit", "cream"]},
    {"id": "p15", "name": "Black ankle boots", "category": "shoes", "price": 159, "stock": 10, "tags": ["cold", "rain", "leather", "black"]},
    {"id": "p16", "name": "Leather tote bag", "category": "accessory", "price": 179, "stock": 6, "tags": ["business", "work", "leather", "brown"]},
    {"id": "p17", "name": "Compact umbrella", "category": "accessory", "price": 25, "stock": 40, "tags": ["rain", "travel", "black"]},
    {"id": "p18", "name": "Grey cashmere scarf", "category": "accessory", "price": 99, "stock": 11, "tags": ["cold", "winter", "cashmere", "grey"]},
    {"id": "p19", "name": "Black pleated midi skirt", "category": "bottom", "price": 79, "stock": 8, "tags": ["business", "elegant", "black"]},
    {"id": "p20", "name": "Olive linen shorts", "category": "bottom", "price": 45, "stock": 14, "tags": ["casual", "summer", "warm", "linen", "olive"]},
    {"id": "p21", "name": "Nude pointed-toe pumps", "category": "shoes", "price": 119, "stock": 9, "tags": ["business", "elegant", "nude"]},
    {"id": "p22", "name": "Olive waterproof parka", "category": "outerwear", "price": 219, "stock": 3, "tags": ["casual", "cold", "rain", "olive"]},
]

FASHION_TRENDS = [
    "Quiet luxury: neutral palettes (camel, grey, navy, cream) and quality fabrics over logos.",
    "Relaxed tailoring: softer blazers worn with knitwear instead of shirts and ties.",
    "Smart sneakers: clean white leather sneakers are accepted in many modern offices.",
    "Layering for travel: a long coat over a fine-gauge knit handles changing weather.",
    "Statement outerwear: trench coats and overcoats are the focal piece of fall/winter looks.",
]

ORDER_HISTORY = {
    "c1": {
        "preferences": "Prefers neutral colors and a clean, minimal style. Size M, shoe size 42.",
        "orders": [
            {"date": "2026-03-14", "product_id": "p02", "name": "White oxford shirt"},
            {"date": "2026-05-02", "product_id": "p10", "name": "Dark indigo slim jeans"},
            {"date": "2026-08-21", "product_id": "p11", "name": "White leather sneakers", "returned": True, "reason": "Too casual for client meetings"},
        ],
    }
}

REVIEWS = {
    "p01": [{"rating": 5, "text": "Sharp fit, works with jeans or trousers."}],
    "p03": [{"rating": 4, "text": "Comfortable for long days, runs slightly long."}],
    "p05": [{"rating": 5, "text": "Needed no break-in, great for walking in the city."}],
    "p06": [{"rating": 5, "text": "Very warm, looks expensive."}, {"rating": 3, "text": "Heavy to pack."}],
    "p07": [{"rating": 5, "text": "Soft and not itchy, perfect under a blazer."}],
    "p11": [{"rating": 4, "text": "Clean look, but a bit casual for formal offices."}],
    "p12": [{"rating": 5, "text": "Kept me dry in a downpour, timeless style."}],
    "p13": [{"rating": 5, "text": "Elegant and wrinkle resistant for travel."}],
    "p15": [{"rating": 2, "text": "Squeaky sole and not fully waterproof."}],
}
