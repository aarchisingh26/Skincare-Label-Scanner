import streamlit as st
from PIL import Image
import pytesseract
import re
from difflib import SequenceMatcher

# === Harmful Ingredients Dictionary ===
harmful_ingredients = {
    "paraben": "Possible endocrine disruptor",
    "sulfate": "Can cause skin irritation",
    "phthalate": "Linked to hormonal issues",
    "formaldehyde": "Known carcinogen",
    "fragrance": "Can cause allergic reactions",
    "hydrogenated rapeseed oil": "Linked to possible allergenic reactions",
    "jojoba seed oil": "Generally safe, but may cause irritation in sensitive individuals or if contaminated",
    "mineral oil": "Can clog pores and cause acne",
    "petrolatum": "May block pores, possible contamination concerns",
    "propylene glycol": "Can cause irritation and allergic reactions",
    "butylated hydroxyanisole (BHA)": "Potential carcinogen and hormone disruptor",
    "butylated hydroxytoluene (BHT)": "Potential allergen and endocrine disruptor",
    "coal tar": "Known carcinogen",
    "triclosan": "Antibacterial linked to hormone disruption",
    "benzophenone": "Possible hormone disruptor and allergen",
    "oxybenzone": "Common sunscreen ingredient linked to hormone disruption",
    "toluene": "Toxic, linked to neurological damage",
    "synthetic colors": "May cause allergic reactions and skin irritation",
    "synthetic dyes": "Linked to allergies and skin irritation",
    "sodium lauryl sulfate (SLS)": "Harsh detergent causing irritation",
    "sodium laureth sulfate (SLES)": "Can cause irritation and contamination with carcinogens",
    "alcohol denat": "Drying and irritating to skin",
    "ethylene oxide": "Potential carcinogen",
    "methylisothiazolinone": "Common allergen",
    "resorcinol": "Skin irritant and potential endocrine disruptor",
    "talc": "Contamination with asbestos risk",
    "benzalkonium chloride": "Can cause irritation",
    "ammonium lauryl sulfate": "Irritating detergent",
    "hydroquinone": "Possible carcinogen, skin irritant",
}

# === Good Ingredients Dictionary ===
good_ingredients = {
    "hyaluronic acid": "Excellent humectant for hydration",
    "niacinamide": "Supports skin barrier, reduces inflammation",
    "ceramide": "Restores skin barrier and retains moisture",
    "vitamin c": "Brightens skin and provides antioxidant protection",
    "vitamin e": "Soothes and protects skin with antioxidant benefits",
    "aloe vera": "Soothing, anti-inflammatory, and hydrating",
    "green tea extract": "Rich in antioxidants and anti-inflammatory",
    "panthenol": "Moisturizing and soothing (provitamin B5)",
    "zinc oxide": "Sun protection and calming for skin",
    "squalane": "Lightweight moisturizer and antioxidant",
    "peptides": "Support skin structure and improve elasticity",
    "colloidal oatmeal": "Soothes irritation and inflammation",
    "licorice root extract": "Brightens skin and reduces redness"
}

def is_close_match(a, b, threshold=0.82):
    return SequenceMatcher(None, a, b).ratio() >= threshold

def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def parse_ingredients(text):
    if not text:
        return []

    # Find ingredients section (case-insensitive)
    match = re.search(r"ingredients[:\-]?\s*(.*)", text, re.IGNORECASE)
    if match:
        ingredients_text = match.group(1)
    else:
        ingredients_text = text

    # Remove text after common section headers
    ingredients_text = re.split(r"(directions|warnings|usage|storage|keep out of reach)", ingredients_text, flags=re.IGNORECASE)[0]
    # Clean punctuation
    ingredients_text = re.sub(r"[\.\);\[\]]+", "", ingredients_text)
    ingredients_text = re.sub(r"\s{2,}", " ", ingredients_text)

    # Split by commas or 'and'
    raw_ingredients = re.split(r",|\band\b", ingredients_text, flags=re.IGNORECASE)
    cleaned_ingredients = [i.strip() for i in raw_ingredients if i.strip()]
    return cleaned_ingredients

def analyze_ingredients(ingredients_list, reference_dict):
    flagged = []
    for ingredient in ingredients_list:
        ingredient_lower = ingredient.lower()
        for ref in reference_dict:
            if ref in ingredient_lower or is_close_match(ingredient_lower, ref.lower()):
                flagged.append({"ingredient": ingredient, "info": reference_dict[ref]})
                break
    return flagged

# --- Streamlit UI ---
st.set_page_config(page_title="Skincare Label Scanner", layout="centered")

st.title("🧴 Skincare Label Scanner")
st.markdown("""
Upload a photo of your skincare product label and get a detailed analysis of its ingredients.
We highlight potentially harmful ingredients, common allergens, and beneficial components.
""")

uploaded_file = st.file_uploader("Upload skincare label image", type=["jpg","jpeg","png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    with st.spinner("Running OCR and analyzing ingredients..."):
        ocr_text = extract_text_from_image(image)
        ingredients = parse_ingredients(ocr_text)
        harmful = analyze_ingredients(ingredients, harmful_ingredients)
        good = analyze_ingredients(ingredients, good_ingredients)

    st.subheader("Extracted Ingredients List")
    if ingredients:
        st.write(", ".join(ingredients))
    else:
        st.write("No ingredients found or could not parse.")

    if harmful:
        st.subheader("⚠️ Potentially Harmful Ingredients Found")
        for item in harmful:
            st.markdown(f"- **{item['ingredient']}**: {item['info']}")
    else:
        st.success("No harmful ingredients detected.")

    if good:
        st.subheader("✅ Beneficial Ingredients Detected")
        for item in good:
            st.markdown(f"- **{item['ingredient']}**: {item['info']}")

    st.subheader("Full OCR Text Output")
    st.text_area("", ocr_text, height=200)

else:
    st.info("Upload an image to start scanning your skincare label.")
