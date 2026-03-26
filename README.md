Here’s a clear, beginner-friendly `README.md` for your RAG project, designed to explain what it does, how it works, and how someone can run it from scratch.

---

## 📄 `README.md`

````markdown
# 🧠 RAG-Food: Simple Retrieval-Augmented Generation with ChromaDB + Ollama

This is a **minimal working RAG (Retrieval-Augmented Generation)** demo using:

- ✅ Local LLM via [Ollama](https://ollama.com/)
- ✅ Local embeddings via `mxbai-embed-large`
- ✅ [ChromaDB](https://www.trychroma.com/) as the vector database
- ✅ A simple food dataset in JSON (Indian foods, fruits, etc.)

---

## 🎯 What This Does

This app allows you to ask questions like:

- “Which Indian dish uses chickpeas?”
- “What dessert is made from milk and soaked in syrup?”
- “What is masala dosa made of?”

It **does not rely on the LLM’s built-in memory**. Instead, it:

1. **Embeds your custom text data** (about food) using `mxbai-embed-large`
2. Stores those embeddings in **ChromaDB**
3. For any question, it:
   - Embeds your question
   - Finds relevant context via similarity search
   - Passes that context + question to a local LLM (`llama3.2`)
4. Returns a natural-language answer grounded in your data.

---

## 📦 Requirements

### ✅ Software

- Python 3.8+
- Ollama installed and running locally
- ChromaDB installed

### ✅ Ollama Models Needed

Run these in your terminal to install them:

```bash
ollama pull llama3.2
ollama pull mxbai-embed-large
````

> Make sure `ollama` is running in the background. You can test it with:
>
> ```bash
> ollama run llama3.2
> ```

---

## 🛠️ Installation & Setup

### 1. Clone or download this repo

```bash
git clone https://github.com/yourname/rag-food
cd rag-food
```

### 2. Install Python dependencies

```bash
pip install chromadb requests
```

### 3. Run the RAG app

```bash
python rag_run.py
```

If it's the first time, it will:

* Create `foods.json` if missing
* Generate embeddings for all food items
* Load them into ChromaDB
* Run a few example questions

---

## 📁 File Structure

```
rag-food/
├── rag_run.py       # Main app script
├── foods.json       # Food knowledge base (created if missing)
├── README.md        # This file
```

---

## 🧠 How It Works (Step-by-Step)

1. **Data** is loaded from `foods.json`
2. Each entry is embedded using Ollama's `mxbai-embed-large`
3. Embeddings are stored in ChromaDB
4. When you ask a question:

   * The question is embedded
   * The top 1–2 most relevant chunks are retrieved
   * The context + question is passed to `llama3.2`
   * The model answers using that info only

---

## 🔍 Try Custom Questions

You can update `rag_run.py` to include your own questions like:

```python
print(rag_query("What is tandoori chicken?"))
print(rag_query("Which foods are spicy and vegetarian?"))
```

---

## 🚀 Next Ideas

* Swap in larger datasets (Wikipedia articles, recipes, PDFs)
* Add a web UI with Gradio or Flask
* Cache embeddings to avoid reprocessing on every run

---

## 👨‍🍳 Credits

Made by Callum using:

* [Ollama](https://ollama.com)
* [ChromaDB](https://www.trychroma.com)
* [mxbai-embed-large](https://ollama.com/library/mxbai-embed-large)
* Indian food inspiration 🍛

'name': 'Adobo sa Gata',
        'category': 'Main Course',
        'origin': 'Philippines',
        'description': 'Adobo sa Gata is a creamy Filipino stew where chicken or pork is braised in coconut milk and simmered with vinegar, garlic, soy sauce, and pepper. This variant provides rich savory and slightly sweet flavors and is a signature of Bicol regional cuisine.',
        'ingredients': 'chicken or pork, coconut milk, vinegar, soy sauce, garlic, bay leaves, pepper, onion, chili',
        'preparation': 'Marinate protein, sauté aromatics, add liquids and simmer until tender, add coconut milk and finish with seasoning.',
        'nutrition': 'Protein-rich with medium fats from coconut, iron, B vitamins. Good source of energy and immune-supporting micronutrients.',
        'cultural_significance': 'Regional Bicol comfort dish served in Filipino celebrations; highlights coconut practices in the Philippines.',
        'dietary': ['gluten-free', 'dairy-free']
    },
    {
        'name': 'Sinigang na Bagnet',
        'category': 'Main Course',
        'origin': 'Philippines',
        'description': 'Sinigang na Bagnet is a Filipino sour soup featuring crispy pork belly in a tamarind-based broth with vegetables like kangkong and radish. The crunchy bagnet and sour broth create a unique texture and flavor contrast.',
        'ingredients': 'pork belly, tamarind, tomatoes, radish, okra, kangkong, fish sauce, onion, garlic',
        'preparation': 'Boil pork and vegetables, deep-fry pork belly, add sour broth, combine and serve hot.',
        'nutrition': 'Offers protein, vitamins, and minerals; high in fat so consume in moderation.',
        'cultural_significance': 'Popular in Ilocos and North Luzon as festive meal; symbol of Filipino sour soup heritage.',
        'dietary': ['gluten-free', 'dairy-free']
    },
    {
        'name': 'Laing',
        'category': 'Main Course',
        'origin': 'Philippines',
        'description': 'Laing is a Philippine dish of dried taro leaves simmered in coconut milk, chili, and shrimp paste. It is creamy, spicy, and deeply comforting, especially in rainy weather.',
        'ingredients': 'dried taro leaves, coconut milk, coconut cream, chili, garlic, onion, ginger, shrimp paste',
        'preparation': 'Sauté aromatics, add coconut milk, add taro leaves, simmer slowly until tender.',
        'nutrition': 'High in fiber, vitamin A, healthy fats; provides calcium and potassium.',
        'cultural_significance': 'Bicolana classic served for fiestas and daily meals among Filipinos.',
        'dietary': ['gluten-free', 'vegetarian-option']
    },
    {
        'name': 'Pancit Bihon Guisado',
        'category': 'Main Course',
        'origin': 'Philippines',
        'description': 'Pancit Bihon is stir-fried rice noodles with meat, seafood, and vegetables. It is served on birthdays and celebrations to represent longevity and prosperity.',
        'ingredients': 'rice noodles, chicken, shrimp, cabbage, carrots, green beans, onion, garlic, soy sauce, calamansi',
        'preparation': 'Soak noodles, stir-fry protein and veggies, add sauce and noodles, toss until done.',
        'nutrition': 'Provides carbohydrates, lean protein and veggie nutrients; moderate sodium.',
        'cultural_significance': 'Birthday staple in Filipino meals representing long life.',
        'dietary': ['gluten-free-option', 'dairy-free']
    },
    {
        'name': 'Halo-Halo',
        'category': 'Dessert',
        'origin': 'Philippines',
        'description': 'Halo-Halo is a Filipino dessert of layered shaved ice, sweet beans, fruits, and milk often topped with ube ice cream. It is a symbol of summer and cultural diversity in ingredients.',
        'ingredients': 'shaved ice, evaporated milk, sweet beans, jackfruit, coconut strips, nata de coco, ube halaya, leche flan, fruits',
        'preparation': 'Layer ingredients in a tall glass, top with ice and milk, and add toppings.',
        'nutrition': 'High in carbohydrates and sugar; includes fiber and antioxidants from fruits and beans.',
        'cultural_significance': 'Widely enjoyed street and restaurant dessert; signifies Filipino joy and kaleidoscopic food culture.',
        'dietary': ['vegetarian', 'gluten-free']
    },
    {
        'name': 'Kale Beet Super Bowl',
        'category': 'Main Course',
        'origin': 'PH Health Trend',
        'description': 'A nutrient-dense bowl of kale, roasted beets, quinoa, avocado, and sunflower seeds in lemon-tahini dressing. Designed to support energy, digestion, and leafy-green intake.',
        'ingredients': 'kale, beets, quinoa, avocado, chickpeas, lemon, tahini, olive oil, garlic',
        'preparation': 'Roast beets, cook quinoa, assemble ingredients, drizzle dressing.',
        'nutrition': 'High in fiber, vitamins K/A/C, plant protein, and healthy fat; low sugar.',
        'cultural_significance': 'Modern wellness bowl inspired by global clean-eating and local produce.',
        'dietary': ['vegan', 'gluten-free']
    },
    {
        'name': 'Mung Bean Sweet Potato Stew',
        'category': 'Main Course',
        'origin': 'PH Health Trend',
        'description': 'Hearty stew of mung beans and sweet potatoes in light spiced coconut broth, high in fiber and complex carbs.',
        'ingredients': 'mung beans, sweet potato, spinach, onion, garlic, ginger, coconut milk, turmeric, cumin',
        'preparation': 'Simmer beans and veg with spices until tender, finish with greens.',
        'nutrition': 'Excellent fiber, protein, and beta-carotene; low fat and nutrient-rich.',
        'cultural_significance': 'Fusion of Filipino and Southeast Asian wholesome cooking.',
        'dietary': ['vegan', 'gluten-free', 'dairy-free']
    },
    {
        'name': 'Chia Seed Overnight Pudding',
        'category': 'Breakfast',
        'origin': 'Global Health',
        'description': 'No-cook breakfast pudding made from chia seeds, almond milk, berries, and nuts; provides omega-3s and sustained energy.',
        'ingredients': 'chia seeds, almond milk, berries, nuts, cinnamon, honey',
        'preparation': 'Mix ingredients, refrigerate overnight, top with fresh fruit.',
        'nutrition': 'High in omega-3, fiber, protein; low in saturated fat.',
        'cultural_significance': 'Modern superfood trend adapted for Filipino healthy diets.',
        'dietary': ['vegan', 'gluten-free', 'dairy-free']
    },
    {
        'name': 'Grilled Salmon with Asparagus',
        'category': 'Main Course',
        'origin': 'Global Health',
        'description': 'Oven-grilled salmon and asparagus with lemon zest and garlic; ideal for balanced macros and heart health.',
        'ingredients': 'salmon, asparagus, olive oil, garlic, lemon, salt, pepper',
        'preparation': 'Season, grill/bake until tender, serve with lemon.',
        'nutrition': 'High omega-3, protein, vitamin A/C, potassium.',
        'cultural_significance': 'Popular in diet-focused meal prep communities.',
        'dietary': ['pescatarian', 'gluten-free']
    },
    {
        'name': 'Lentil Mushroom Meatloaf',
        'category': 'Main Course',
        'origin': 'Global Health',
        'description': 'Plant-based meatloaf using lentils and mushrooms for umami; topped with tomato glaze and baked to sliceable texture.',
        'ingredients': 'lentils, mushrooms, onion, carrot, oats, flaxseed meal, tomato paste, spices',
        'preparation': 'Mix, shape loaf, bake 45 mins, glaze during last 10 mins.',
        'nutrition': 'High protein, high fiber, low saturated fats, plant micronutrients.',
        'cultural_significance': 'Used for vegetarian family dinners and flexible meal planning.',
        'dietary': ['vegan', 'gluten-free-option']
    },
    {
        'name': 'Spanish Seafood Paella',
        'category': 'Main Course',
        'origin': 'Spain',
        'description': 'Large pan rice dish with saffron, mussels, clams, shrimp, and chicken cooked using socarrat technique for crisp bottom layer.',
        'ingredients': 'paella rice, saffron, chicken, seafood, peas, bell pepper, onion, garlic, tomato, stock',
        'preparation': 'Sauté base, add rice and stock, place seafood, cook until stock absorbed and crust forms.',
        'nutrition': 'Balanced protein and carbs, low saturated fat, rich in seafood minerals.',
        'cultural_significance': 'Shared festive dish in Spanish regional gatherings.',
        'dietary': ['pescatarian']
    },
    {
        'name': 'Italian Osso Buco',
        'category': 'Main Course',
        'origin': 'Italy',
        'description': 'Slow-braised veal shank with aromatics and white wine, served with gremolata and risotto for a classic Milanese experience.',
        'ingredients': 'veal shank, carrot, celery, onion, garlic, tomatoes, wine, broth, herbs',
        'preparation': 'Brown meat, braise in liquid 2-3 hours, finish with zesty gremolata.',
        'nutrition': 'Rich protein, minerals, moderate fat, collagen benefits.',
        'cultural_significance': 'Featured in traditional Italian Sunday meals and special occasions.',
        'dietary': ['gluten-free']
    },
    {
        'name': 'Japanese Ramen',
        'category': 'Main Course',
        'origin': 'Japan',
        'description': 'Ramen in slow-simmered broth with noodles, egg, and vegetables. Broth style varieties include shoyu, miso, tonkotsu, delivering deep umami and comfort.',
        'ingredients': 'ramen noodles, pork bones, chicken bones, soy sauce, miso, garlic, ginger, eggs, nori',
        'preparation': 'Simmer stock for hours, cook noodles, broth, assemble toppings.',
        'nutrition': 'High in protein and carbs; sodium can be high.',
        'cultural_significance': 'Staple of Japanese culinary street food culture with regional styles.',
        'dietary': ['dairy-free']
    },
    {
        'name': 'French Ratatouille',
        'category': 'Main Course',
        'origin': 'France',
        'description': 'Layered baked vegetables with herbs and tomato sauce; a Provençal classic that highlights seasonal produce and slow-cooking technique.',
        'ingredients': 'eggplant, zucchini, tomatoes, bell peppers, onion, garlic, olive oil, thyme, basil',
        'preparation': 'Sauté base, arrange sliced vegetables in dish, bake covered then uncovered.',
        'nutrition': 'Low-calorie, vitamin-rich, fiber-heavy, antioxidant-packed.',
        'cultural_significance': 'A symbol of southern French peasant cuisine and garden cooking.',
        'dietary': ['vegan', 'gluten-free']
    },
    {
        'name': 'Mexican Carne Asada Tacos',
        'category': 'Main Course',
        'origin': 'Mexico',
        'description': 'Grilled marinated beef slices served on corn tortillas with cilantro, onion, and salsa. The grill method imparts char and smoky flavor.",
        'ingredients': 'flank steak, lime, orange juice, garlic, cumin, chili, tortillas, onion, cilantro, salsa',
        'preparation': 'Marinate overnight, grill high heat, rest and slice, assemble tacos.',
        'nutrition': 'High protein, moderate fat, contains vitamin C from citrus marinade.',
        'cultural_significance': 'Iconic street food representing Mexican carne asada culture.',
        'dietary': ['gluten-free', 'dairy-free']
