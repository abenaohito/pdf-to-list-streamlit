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
            while i + 1 < len(lines):
                upper = lines[i]
                lower = lines[i+1]

                # 上段にロケーション + JAN + 数量、下段に商品情報
                match_upper = re.match(r'^(M\d{3})\s+\d+\s+(\d{3})\s+([\d,]+)$', upper)
                match_lower = re.search(r'(S\d{3}.*?)（?AS240', lower)

                if match_upper and match_lower:
                    location = match_upper.group(1)
                    jan = match_upper.group(2)
                    quantity = int(match_upper.group(3).replace(',', ''))
                    product = match_lower.group(1)
                    cases = quantity // 240

                    extracted.append({
                        "ロケーション": location,
                        "JAN下3桁": jan,
                        "商品": product,
                        "数量": quantity,
                        "ケース数": cases,
                        "パレットNo": ""
                    })
                    i += 2
                else:
                    i += 1

    if extracted:
        df = pd.DataFrame(extracted)
        st.success("✅ データ抽出完了！ 下記リストをコピーしてご利用ください。")
        st.dataframe(df, use_container_width=True)

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
