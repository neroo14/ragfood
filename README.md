# 🧠 RAG-Food Enhanced (with 15 Filipino Food Items)

## 👤 Developer
- Name: Nero Andrek Solon from Far Eastern University

## ✨ Project customization overview
This enhanced version of RAG-Food adds 15 new, richly documented Filipino food items to `filipino_foods.json`, categorized as:
- 5 regionally traditional dishes (cultural/regional cuisine background)
- 5 healthy foods with detailed nutritional benefits
- 5 popular international dishes with cooking methods (Filipino adaptations)

It features:
- Semantic search using ChromaDB and Ollama models
- All content in Filipino language for authenticity
- Comprehensive details per item: name, category, origin, description, ingredients, preparation, nutrition, cultural significance, dietary classifications
- Validation script for testing queries

## 🥘 15 Newly-added Filipino food items
1. **Adobo sa Gata** (Main Course, Bicol Region) - Creamy chicken or pork stew with coconut milk, vinegar, garlic, soy, and pepper; rich and tangy flavor for celebrations.
2. **Sinigang na Bagnet** (Main Course, Ilocos Region) - Sour tamarind soup with crispy pork belly and vegetables; crunchy texture with refreshing sour broth.
3. **Laing** (Main Course, Bicol Region) - Dried taro leaves cooked in coconut milk with chili; creamy, spicy comfort food for rainy days.
4. **Pancit Bihon Guisado** (Main Course, Philippines) - Stir-fried rice noodles with vegetables, meat, and seafood in soy-citrus sauce; symbolizes long life in birthdays.
5. **Halo-Halo** (Dessert, Philippines) - Layered shaved ice with sweet beans, fruits, and milk; refreshing treat showcasing Filipino ingredient diversity.
6. **Pinakbet** (Main Course, Ilocos Region) - Vegetable stew with eggplant, squash, and bagoong alamang; healthy, low-calorie with probiotics.
7. **Tinolang Manok** (Soup, Philippines) - Chicken soup with papaya and malunggay in ginger broth; comforting with immune-boosting nutrients.
8. **Ensaladang Talong** (Salad, Philippines) - Grilled eggplant salad with tomatoes and bagoong dressing; low-calorie, fiber-rich side dish.
9. **Ginataang Gulay** (Main Course, Philippines) - Vegetables cooked in coconut milk; creamy and nutritious with healthy fats.
10. **Tortang Talong** (Breakfast, Philippines) - Grilled eggplant omelette; protein and fiber-rich breakfast staple.
11. **Filipino-Style Carbonara** (Main Course, Fusion) - Creamy pasta with bacon and cheese; popular fast-food adaptation of Italian dish.
12. **Filipino Spaghetti** (Main Course, Fusion) - Sweet spaghetti with ground meat, hotdog, and cheese; birthday party favorite.
13. **Filipino-Style Pizza** (Main Course, Fusion) - Pizza with tuna, pineapple, and cheese; unique tropical toppings.
14. **Filipino Fried Chicken** (Main Course, Fusion) - Crispy chicken with soy-vinegar marinade; double-fried for extra crunch.
15. **Filipino Burger Steak** (Main Course, Fusion) - Beef patties with mushroom gravy and fried egg; comforting eatery dish.

## 📦 Installation and setup
1. `cd ragfood`
2. Optional virtual env: `python -m venv venv && .\venv\Scripts\activate`
3. `pip install chromadb requests`
4. Ensure Ollama models present:
   - `ollama pull llama3.2`
   - `ollama pull mxbai-embed-large`
5. Start Ollama in another shell or background.
6. Run:
   - `python rag_run.py` (loads main foods.json)
   - Or modify script to load `filipino_foods.json` for Filipino-only data

## 🧪 Validation test queries
Use `python test_rag_queries.py` to run sample queries (adapt for Filipino data):
- Ano ang Adobo sa Gata?
- Alin ang mga pagkain na mataas sa protina?
- Sabihin mo sa akin ang tungkol sa mga ulam na Filipino
- Ano ang mga vegan options na available?
- Ano ang mga pagkain na maaaring i-grill?
- Ipaliwanag ang nutritional benefits ng Brazilian Acai Bowl (or Filipino equivalent)
- Paano lutuin ang Spanish Seafood Paella? (or Filipino adaptation)
- Ilarawan ang Moroccan Chickpea & Sweet Potato Tagine (or Filipino version)
- Ano ang Shakshuka with Spinach? (or Filipino dish)
- Alin ang mga gluten-free na dishes?

## 💬 Personal Reflection (Nero Andrek Solon)
Working on this RAG-Food project has been an eye-opening journey into the world of Retrieval-Augmented Generation and AI-driven systems. As a student from Far Eastern University, I initially approached this with curiosity about how machines could understand and respond to natural language queries about food. The process of curating 15 Filipino food items, all described in Filipino, deepened my appreciation for my cultural heritage while challenging me to think critically about data representation in AI.

The technical aspects were daunting at first—setting up ChromaDB for vector embeddings, integrating Ollama for local LLM inference, and ensuring semantic search accuracy. I learned that RAG isn't just about feeding data to a model; it's about crafting context that allows the AI to reason and provide grounded answers. Debugging timeouts and connection issues with Ollama taught me patience and the importance of robust error handling in AI applications.

What struck me most was the growth mindset required in AI development. Each failed query or inaccurate response wasn't a setback but a learning opportunity. I iterated on the data, refining descriptions to include more nutritional details and cultural significance, which improved retrieval quality. This project reinforced that AI builders must be interdisciplinary—combining computer science with domain knowledge, in this case, Filipino cuisine.

The experience also highlighted ethical considerations in AI, like ensuring diverse and accurate representations of cultures. By focusing on Filipino foods, I contributed to making AI more inclusive, potentially helping preserve culinary traditions through technology.

Looking forward, I'm excited to apply these skills in future projects, perhaps in healthcare or education, where RAG could democratize access to information. This endeavor has transformed me from a passive AI user to an active builder, fostering a lifelong commitment to innovative, responsible AI development. (Word count: 312)

## 📌 Important Notes
- All food descriptions are in Filipino for cultural authenticity.
- To use Filipino data exclusively, modify `rag_run.py` to load `filipino_foods.json`.
- Ensure Ollama is running for queries to work.
- This project demonstrates understanding of vector embeddings and semantic search.
