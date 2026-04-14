import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- Function lấy reaction ---
def get_facebook_reactions(driver, url):
    wait = WebDriverWait(driver, 10)
    try:
        driver.get(url)

        anchor = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(),'reaction')]")
            )
        )

        spans = anchor.find_elements(By.XPATH, "following-sibling::span//span")

        raw_text = spans[-1].get_attribute("textContent").strip()

        return int(raw_text.replace(",", ""))

    except:
        return None


# --- Setup Streamlit ---
st.title("🔥 Facebook Reaction Scraper")

uploaded_file = st.file_uploader("Upload file CSV hoặc Excel", type=["csv", "xlsx"])

if uploaded_file:
    # Đọc file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Preview data:", df.head())

    if st.button("🚀 Bắt đầu crawl"):
        # Setup headless browser
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=options)

        results = []

        progress = st.progress(0)

        for i, row in df.iterrows():
            link = row["link"]

            reaction = get_facebook_reactions(driver, link)
            results.append(reaction)

            progress.progress((i + 1) / len(df))

        driver.quit()

        df["reaction"] = results

        st.success("✅ Hoàn thành!")

        st.write(df)

        # Download file
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download kết quả",
            csv,
            "result.csv",
            "text/csv"
        )