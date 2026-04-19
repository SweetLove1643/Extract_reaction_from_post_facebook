import streamlit as st
import pandas as pd
import time
import random

from crawler import Crawl_wokers  # import class của bạn

st.set_page_config(page_title="Facebook Crawl Tool", layout="wide")

st.title("🚀 Facebook Post Crawler")

# Upload file
uploaded_file = st.file_uploader("📂 Upload CSV/Excel", type=["csv", "xlsx"])

# Input hashtag
hashtag = st.text_input("🔖 Nhập hashtag", "#FITUTE")

# Button
start = st.button("🔥 Bắt đầu crawl")

if start and uploaded_file:
    # đọc file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    if "link_post" not in df.columns:
        st.error("❌ File phải có cột 'link_post'")
        st.stop()

    # tạo cột
    columns = ["reaction", "share", "caption", "hashtag_valid", "is_public", "error"]
    for col in columns:
        if col not in df.columns:
            df[col] = None

    crawler = Crawl_wokers()

    progress_bar = st.progress(0)
    status_text = st.empty()

    total = len(df)

    for i, row in df.iterrows():
        url = str(row["link_post"]).strip()

        if not url or url == "nan":
            continue

        status_text.text(f"🚀 Crawling {i+1}/{total}")

        result = crawler.crawl_post(url, hashtag)

        df.at[i, "reaction"] = result["reaction"]
        df.at[i, "share"] = result["share"]
        df.at[i, "caption"] = result["caption"]
        df.at[i, "hashtag_valid"] = result["hashtag"]
        df.at[i, "is_public"] = result["is_public"]
        df.at[i, "error"] = result["error"]

        progress_bar.progress((i + 1) / total)

        time.sleep(random.uniform(1.5, 3))

    crawler.driver.quit()

    st.success("🔥 Crawl hoàn tất!")

    st.dataframe(df)

    # download
    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "📥 Download kết quả",
        data=csv,
        file_name="output.csv",
        mime="text/csv"
    )