import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

st.set_page_config(page_title="PDF集約リスト変換", layout="wide")
st.title("📄 PDF → 集約リスト変換ツール")

uploaded_file = st.file_uploader("PDFファイルをアップロード", type="pdf")

if uploaded_file:
    extracted = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            lines = page.extract_text().split("\n")
            buffer = None

            for line in lines:
                line = line.strip()

                # 1行目: ロケーション + JAN + 数量行（例: M013 2 105 2,160）
                if re.match(r'^M\d{3}\s+\d+\s+\d{3}\s+[\d,]+$', line):
                    parts = line.split()
                    location = parts[0]
                    jan = parts[2]
                    quantity = int(parts[3].replace(',', ''))
                    buffer = {
                        "ロケーション": location,
                        "JAN下3桁": jan,
                        "数量": quantity
                    }

                # 2行目: 商品コード + 商品名 + (AS240)
                elif buffer and re.search(r'(S\d{3}.*?)（AS240', line):
                    product_match = re.search(r'(S\d{3}.*?)（AS240', line)
                    if product_match:
                        buffer["商品"] = product_match.group(1)
                        buffer["ケース数"] = buffer["数量"] // 240
                        buffer["パレットNo"] = ""
                        extracted.append(buffer)
                        buffer = None

    if extracted:
        df = pd.DataFrame(extracted, columns=["ロケーション", "JAN下3桁", "商品", "数量", "ケース数", "パレットNo"])
        st.success("✅ データ抽出完了！ 下記リストをコピーしてご利用ください。")
        st.dataframe(df, use_container_width=True)

        # Excel出力（任意）
        to_excel = io.BytesIO()
        df.to_excel(to_excel, index=False, sheet_name="集約リスト")
        to_excel.seek(0)

        st.download_button(
            label="📥 Excelでダウンロード",
            data=to_excel,
            file_name="集約リスト.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("❗ データを抽出できませんでした。PDFのフォーマットをご確認ください。")
