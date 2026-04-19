import time
import random
import pandas as pd
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Crawl_wokers():
    def __init__(self):
        self.options = None
        self.driver = None

        self.options = Options()
        # self.options.add_argument("--headless=new")  # bỏ nếu muốn debug
        # self.options.add_argument("--disable-gpu")
        # self.options.add_argument("--window-size=1920,1080")
        # self.options.add_argument("--lang=vi-VN")

        # self.driver = webdriver.Chrome(options=self.options)

        # ⚠️ bắt buộc cho cloud
        self.options.add_argument("--headless=new")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")

        # 👇 dùng webdriver-manager
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )

        pass

    # 🎯 helper: lấy text an toàn
    def safe_text(self, element):
        try:
            return element.text.strip()
        except:
            return None
    
    # 🎯 helper: convert 1.2K -> 1200
    def normalize_number(self, text):
        if not text:
            return None

        text = text.replace(",", "").strip().upper()

        if "K" in text:
            return int(float(text.replace("K", "")) * 1000)
        if "M" in text:
            return int(float(text.replace("M", "")) * 1_000_000)

        try:
            return int(text)
        except:
            return None

    # ❤️ REACTION //done
    def get_reaction(self, body, link_post):
        try:
            # ⚡ cách 1: tìm theo text
            reaction_el = body.find_element(
                By.XPATH,
                "//span[@class='x135b78x']"
            )
            number_react = self.normalize_number(reaction_el.text)
            print(f"Lấy thành công số lượng reaction từ {link_post} với số lượng: {number_react}")
            return number_react
        except:
            print(f"Thất bại khi thực hiện get_reaction với post_url: {link_post}")
            return None

    # 🔁 SHARE //skip
    def get_share(self, body, link_post):
        try:
            share_elements = body.find_elements(
                By.XPATH,
                "//span[contains(text(),'chia sẻ') or contains(text(),'share')]"
            )

            for el in share_elements:
                text = el.text.lower()

                # ví dụ: "4 lượt chia sẻ"
                number = re.findall(r"\d+\.?\d*[kKmM]?", text)

                if number:
                    share_count = self.normalize_number(number[0])
                    print(f"✅ Share {link_post}: {share_count}")
                    return share_count

            return 0

        except Exception as e:
            print(f"❌ Lỗi get_share | {link_post} | {e}")
            return None

    # 📝 CAPTION //done
    def get_caption(self, body, link_post)->str:
        try:
            el = body.find_element(
                By.XPATH,
                "//div[@data-ad-preview='message']"
            )
            print(f"Lấy thành công caption từ:{link_post}")
            return el.text.strip()
        except:
            print(f"Thất bại khi thực hiện get_caption với post_url: {link_post}")
            return None

    # #️⃣ HASHTAG // chưa kiểm tra
    def have_hashtag(self, 
                     body, 
                     link_post, 
                     hashtag: str
        ):
        try:
            if not hashtag:
                print(f"Tham số hashtag = None khi kiểm tra hashtag với link_url{link_post}")
                return False

            caption = self.get_caption(body, link_post)
            if not caption:
                return False
            
            hashtag = hashtag.lower().replace("#", "")
            caption = caption.lower().replace("#", "")
            if hashtag in caption:
                print(f"Kiểm tra hashtag thành công ở {link_post}, với giá trị True")
                return True
            else:
                print(f"Kiểm tra hashtag thành công ở {link_post}, với giá trị False")
                return False

        except:
            print(f"Thất bại khi thực hiện kiểm tra hashtag với post_url: {link_post}")
            return None

    # 🌍 PUBLIC POST
    def post_public(self, body, link_post) -> bool:
        try:
            # icon public thường có aria-label
            parents = body.find_elements(
                By.XPATH,
                "//span[contains(@class,'xuxw1ft')]"
            )

            for p in parents:
                svgs = p.find_elements(By.XPATH, ".//*[name()='svg']")

                if not svgs:
                    continue

                svg = svgs[0]

                title = svg.get_attribute("title")

                if not title:
                    try:
                        title = svg.find_element(By.XPATH, ".//title").text
                    except:
                        title = ""

                title = title.lower()
                if "công khai" in title or "public" in title or "đã chia sẻ với công khai" in title:
                    print(f"Kiểm tra thành công post_public từ {link_post}")
                    return True
            
            return False               
            
        except Exception as e:
            print(f"Lỗi post_public | {link_post} | {e}")
            print(f"Thất bại khi thực hiện kiểm tra post_public với post_url: {link_post}")
            return None

    def crawl_post(self, url, hashtag):
        try:
            self.driver.get(url)
            # delay sau load
            time.sleep(random.uniform(2, 4))

            # scroll nhẹ
            self.driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(random.uniform(1, 2))

            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            body = self.driver.find_element(By.TAG_NAME, "body")

            reaction = self.get_reaction(body, url)
            share = self.get_share(body, url)
            caption = self.get_caption(body, url)
            has_tag = self.have_hashtag(body, url, hashtag)
            is_public = self.post_public(body, url)

            return {
                "reaction": reaction,
                "share": share,
                "caption": caption,
                "hashtag": has_tag,
                "is_public": is_public,
                "error": None
            }

        except Exception as e:
            return {
                "reaction": None,
                "share": None,
                "caption": None,
                "hashtag": None,
                "is_public": None,
                "error": str(e)
            }



def process_file(input_file, output_file, hashtag):
    crawler = Crawl_wokers()

    # đọc file
    if input_file.endswith(".csv"):
        df = pd.read_csv(input_file)
    else:
        df = pd.read_excel(input_file)

    # đảm bảo có cột link_post
    if "link_post" not in df.columns:
        raise ValueError("File phải có cột 'link_post'")

    # tạo cột mới
    columns = ["reaction", "share", "caption", "hashtag_valid", "is_public", "error"]

    for col in columns:
        if col not in df.columns:
            df[col] = None

    for i, row in df.iterrows():
        url = str(row["link_post"]).strip()

        if not url or url == "nan":
            continue

        print(f"🚀 [{i+1}/{len(df)}] Crawling: {url}")

        result = crawler.crawl_post(url, hashtag)

        df.at[i, "reaction"] = result["reaction"]
        df.at[i, "share"] = result["share"]
        df.at[i, "caption"] = result["caption"]
        df.at[i, "hashtag_valid"] = result["hashtag"]
        df.at[i, "is_public"] = result["is_public"]
        df.at[i, "error"] = result["error"]

        # delay random tránh block
        time.sleep(random.uniform(1.5, 3.5))

    crawler.driver.quit()

    # save file
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print("🔥 DONE! File đã được xuất.")


# process_file(
#     input_file="link.csv",
#     output_file="output.csv",
#     hashtag="#FITUTE"
# )
