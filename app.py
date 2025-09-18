import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO


def parse_section(root, section_tag):
    """특정 태그(section)를 찾아 DataFrame으로 변환"""
    sections = root.findall(f".//{section_tag}")
    records = []
    for idx, elem in enumerate(sections, start=1):
        for child in elem.iter():
            if child.text and child.text.strip():
                record = {
                    "Item": f"{section_tag}{idx}",
                    "Path": f"{section_tag}/{child.tag}",
                    "Tag": child.tag,
                    "Value": child.text.strip(),
                    "Attributes": ", ".join([f"{k}={v}" for k, v in child.attrib.items()])
                }
                records.append(record)
    return pd.DataFrame(records) if records else None


def parse_dataform(root):
    """dataForm 내의 formData를 파싱하여 DataFrame으로 변환"""
    dataform_elements = root.findall(".//dataForm/formData")
    records = []

    for elem in dataform_elements:
        if elem.text and elem.text.strip():
            lines = elem.text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and '=' in line and line.startswith('%') and line.count('%') >= 2:
                    # %KEY%=VALUE 형식 파싱
                    key_end = line.find('%', 1)
                    if key_end > 0:
                        key = line[1:key_end]
                        value = line[key_end + 2:] if len(line) > key_end + 2 else ""

                        record = {
                            "Key": key,
                            "Value": value,
                            "Raw_Line": line
                        }
                        records.append(record)

    return pd.DataFrame(records) if records else None


def compress_xml_to_excel(xml_bytes):
    """XML 파일을 파싱해 Excel 바이트 객체 반환"""
    tree = ET.parse(xml_bytes)
    root = tree.getroot()

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # COMPRESS 주요 섹션
        sections = [
            "generalVesselInfo",
            "heatExchangerGeneralInfo",
            "heatExchangerDesignConditions",
            "pressureChamberConditions",
            "vesselResults",
            "closure1",
            "closure2",
            "nozzle"
        ]
        for sec in sections:
            df = parse_section(root, sec)
            if df is not None and not df.empty:
                df.to_excel(writer, sheet_name=sec[:30], index=False)

        # dataForm 섹션 추가
        df_dataform = parse_dataform(root)
        if df_dataform is not None and not df_dataform.empty:
            df_dataform.to_excel(writer, sheet_name="DataForm_Details", index=False)

        # All_Data 시트 (전체 구조)
        all_records = []
        for sec in sections:
            sec_nodes = root.findall(f".//{sec}")
            for idx, elem in enumerate(sec_nodes, start=1):
                for child in elem.iter():
                    if child.text and child.text.strip():
                        record = {
                            "Item": f"{sec}{idx}",
                            "Path": f"{sec}/{child.tag}",
                            "Tag": child.tag,
                            "Value": child.text.strip(),
                            "Attributes": ", ".join([f"{k}={v}" for k, v in child.attrib.items()])
                        }
                        all_records.append(record)

        # 루트 전체 탐색 (섹션 외 노드도 포함)
        for elem in root.iter():
            if elem.text and elem.text.strip():
                record = {
                    "Item": root.tag,
                    "Path": elem.tag,
                    "Tag": elem.tag,
                    "Value": elem.text.strip(),
                    "Attributes": ", ".join([f"{k}={v}" for k, v in elem.attrib.items()])
                }
                all_records.append(record)

        pd.DataFrame(all_records).to_excel(writer, sheet_name="All_Data", index=False)

    output.seek(0)
    return output


# ---------------- Streamlit UI ----------------
st.title("COMPRESS XML 파서")
st.write("Codeware COMPRESS XML 파일을 업로드하면 내용을 파싱하여 표시하고, Excel 파일로 다운로드할 수 있습니다.")

uploaded_file = st.file_uploader("XML 파일 업로드", type=["xml"])

if uploaded_file is not None:
    st.success("✅ XML 파일 업로드 완료")

    # XML 내용 파싱 (미리보기용)
    xml_bytes = BytesIO(uploaded_file.getvalue())
    tree = ET.parse(xml_bytes)
    root = tree.getroot()

    all_records = []
    for elem in root.iter():
        if elem.text and elem.text.strip():
            record = {
                "Item": root.tag,
                "Path": elem.tag,
                "Tag": elem.tag,
                "Value": elem.text.strip(),
                "Attributes": ", ".join([f"{k}={v}" for k, v in elem.attrib.items()])
            }
            all_records.append(record)

    df_preview = pd.DataFrame(all_records)

    st.subheader("📋 All_Data 미리보기 (상위 100행)")
    st.dataframe(df_preview.head(100))

    # Excel 변환
    excel_data = compress_xml_to_excel(BytesIO(uploaded_file.getvalue()))

    st.download_button(
        label="📥 Excel 다운로드",
        data=excel_data,
        file_name="compress_result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
