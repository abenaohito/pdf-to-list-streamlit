import streamlit as st
import pdfplumber
import pandas as pd
import io
import re

st.set_page_config(page_title="PDF集約リスト変換", layout="wide")
st.title("📄 PDF → 集約リスト変換ツール")

uploaded_file = st.file_uploader("PDFファイルをアップロード", type="pdf")

if uploaded_file:
    extracted = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            lines = [line.strip() for line in page.extract_text().split('\n') if line.strip()]
            i = 0
            while i + 3 < len(lines):
                loc_line = lines[i]
                jan_line = lines[i+1]
                prod_line = lines[i+2]
                qty_line = lines[i+3]

                if re.match(r'^M\d{3}$', loc_line) and jan_line.isdigit() and re.search(r'S\d{3}', prod_line) and re.match(r'^[\d,]+$', qty_line):
                    location = loc_line
                    jan = jan_line[-3:]
                    product_match = re.search(r'(S\d{3}.*?)（?AS240', prod_line)
                    product = product_match.group(1) if product_match else prod_line
                    quantity = int(qty_line.replace(',', ''))
                    cases = quantity // 240
                    extracted.append({
                        "ロケーション": location,
                        "JAN下3桁": jan,
                        "商品": product,
                        "数量": quantity,
                        "ケース数": cases,
                        "パレットNo": ""
                    })
                    i += 4
                else:
                    i += 1

    if extracted:
        df = pd.DataFrame(extracted)
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
