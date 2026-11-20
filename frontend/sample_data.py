"""Synthetic demonstration datasets and receipt images for InvoiceFlow AI.

Generates realistic de-identified Vietnamese medicine invoices and healthcare payment
receipts with matching OCR bounding boxes for instant 1-click frontend demos.
No external network, patient data, or confidential assets required.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


# Font lookup for cross-platform rendering
def _get_font(size: int = 14, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


def generate_clean_medicine_sample() -> tuple[bytes, dict[str, Any]]:
    """Generate a clean 3-medicine invoice with matching OCR geometry and image."""
    width, height = 960, 520
    im = Image.new("RGB", (width, height), "#ffffff")
    d = ImageDraw.Draw(im)

    f_title = _get_font(22, bold=True)
    f_sub = _get_font(13)
    f_hdr = _get_font(14, bold=True)
    f_row = _get_font(14)
    f_tot = _get_font(15, bold=True)

    # Decorative header & clinic info
    d.rectangle([0, 0, width, 8], fill="#3b82f6")
    d.text((40, 24), "PHÒNG KHÁM ĐA KHOA QUỐC TẾ", fill="#1e3a8a", font=f_title)
    d.text((40, 58), "Địa chỉ: 124 Nguyễn Tri Phương, Quận 10, TP. Hồ Chí Minh", fill="#64748b", font=f_sub)
    d.text((40, 78), "Điện thoại: (028) 3829 4567  ·  Mã toa: IF-2026-9914", fill="#64748b", font=f_sub)

    d.line([(40, 110), (width - 40, 110)], fill="#e2e8f0", width=2)
    d.text((width // 2 - 120, 125), "HÓA ĐƠN BÁN LẺ THUỐC", fill="#0f172a", font=f_title)

    # Table Header Box
    y_hdr = 175
    d.rectangle([40, y_hdr - 6, width - 40, y_hdr + 28], fill="#f1f5f9", outline="#cbd5e1", width=1)
    d.text((50, y_hdr), "STT", fill="#334155", font=f_hdr)
    d.text((120, y_hdr), "Tên thuốc / Hàm lượng", fill="#334155", font=f_hdr)
    d.text((475, y_hdr), "SL", fill="#334155", font=f_hdr)
    d.text((560, y_hdr), "ĐVT", fill="#334155", font=f_hdr)
    d.text((650, y_hdr), "Đơn giá (VND)", fill="#334155", font=f_hdr)
    d.text((780, y_hdr), "Thành tiền (VND)", fill="#334155", font=f_hdr)

    # Rows data
    items_def = [
        {
            "stt": 1,
            "ten_dich_vu": "NEWBUTIN SR 300mg",
            "so_luong": 56,
            "don_vi_tinh": "Viên",
            "don_gia": 6955,
            "thanh_tien": 389480,
        },
        {
            "stt": 2,
            "ten_dich_vu": "MEBEVER MR CAPSULES 200mg",
            "so_luong": 56,
            "don_vi_tinh": "Viên",
            "don_gia": 3795,
            "thanh_tien": 212520,
        },
        {
            "stt": 3,
            "ten_dich_vu": "NORMAGUT 250mg",
            "so_luong": 56,
            "don_vi_tinh": "Viên",
            "don_gia": 6955,
            "thanh_tien": 389480,
        },
    ]

    ocr_boxes = []
    items_out = []
    y = 220

    for idx, it in enumerate(items_def):
        row_y = y
        # Draw background alternating row
        if idx % 2 == 1:
            d.rectangle([40, row_y - 6, width - 40, row_y + 30], fill="#f8fafc")
        d.line([(40, row_y + 30), (width - 40, row_y + 30)], fill="#e2e8f0", width=1)

        # Draw texts
        d.text((60, row_y), str(it["stt"]), fill="#1e293b", font=f_row)
        d.text((120, row_y), it["ten_dich_vu"], fill="#1e293b", font=f_row)
        d.text((485, row_y), str(it["so_luong"]), fill="#1e293b", font=f_row)
        d.text((565, row_y), it["don_vi_tinh"], fill="#1e293b", font=f_row)
        d.text((660, row_y), f"{it['don_gia']:,}", fill="#1e293b", font=f_row)
        d.text((795, row_y), f"{it['thanh_tien']:,}", fill="#1e293b", font=f_row)

        # Record exact bounding boxes for each token
        b_stt = [50, row_y - 3, 80, row_y + 24]
        b_name = [115, row_y - 3, 430, row_y + 24]
        b_qty = [475, row_y - 3, 510, row_y + 24]
        b_unit = [555, row_y - 3, 605, row_y + 24]
        b_price = [650, row_y - 3, 730, row_y + 24]
        b_amt = [785, row_y - 3, 885, row_y + 24]

        id_stt = len(ocr_boxes)
        ocr_boxes.append(b_stt)
        id_name = len(ocr_boxes)
        ocr_boxes.append(b_name)
        id_qty = len(ocr_boxes)
        ocr_boxes.append(b_qty)
        id_unit = len(ocr_boxes)
        ocr_boxes.append(b_unit)
        id_price = len(ocr_boxes)
        ocr_boxes.append(b_price)
        id_amt = len(ocr_boxes)
        ocr_boxes.append(b_amt)

        items_out.append(
            {
                "stt": it["stt"],
                "ten_dich_vu": it["ten_dich_vu"],
                "so_luong": it["so_luong"],
                "don_vi_tinh": it["don_vi_tinh"],
                "don_gia": it["don_gia"],
                "thanh_tien": it["thanh_tien"],
                "evidence_box_ids": {
                    "stt": [id_stt],
                    "ten_dich_vu": [id_name],
                    "so_luong": [id_qty],
                    "don_vi_tinh": [id_unit],
                    "don_gia": [id_price],
                    "thanh_tien": [id_amt],
                },
            }
        )
        y += 44

    # Total Row
    total_val = sum(it["thanh_tien"] for it in items_def)  # 991,480
    d.rectangle([40, y + 5, width - 40, y + 45], fill="#eff6ff", outline="#bfdbfe", width=1)
    d.text((120, y + 14), "TỔNG CỘNG TIỀN THANH TOÁN (VND):", fill="#1e3a8a", font=f_tot)
    d.text((770, y + 14), f"{total_val:,} VND", fill="#1e3a8a", font=f_tot)

    box_total = [760, y + 10, 900, y + 40]
    id_tot = len(ocr_boxes)
    ocr_boxes.append(box_total)

    # Footer signature text
    d.text((80, y + 70), "Người lập biểu\n(Ký và ghi rõ họ tên)", fill="#64748b", font=f_sub)
    d.text((width - 240, y + 70), "Dược sĩ tư vấn\n(Ký và ghi rõ họ tên)", fill="#64748b", font=f_sub)

    out = io.BytesIO()
    im.save(out, format="PNG")
    png_bytes = out.getvalue()

    result = {
        "document_type": "MEDICINE_INVOICE",
        "status": "EXTRACTED",
        "qa_status": "PENDING_HUMAN_REVIEW",
        "ready_for_rpa": False,
        "image_size": [width, height],
        "ocr_boxes": ocr_boxes,
        "document_total": {"value": total_val, "box_id": id_tot},
        "total_checks": [
            {
                "field": "thanh_tien",
                "document_total": total_val,
                "rows_sum": total_val,
                "difference": 0,
                "status": "MATCH",
            }
        ],
        "items": items_out,
    }
    return png_bytes, result


def generate_dropped_row_sample() -> tuple[bytes, dict[str, Any]]:
    """Reconstruct synthetic document with missing row 3 (exercises mismatch detection)."""
    width, height = 960, 520
    im = Image.new("RGB", (width, height), "#ffffff")
    d = ImageDraw.Draw(im)

    f_title = _get_font(22, bold=True)
    f_sub = _get_font(13)
    f_hdr = _get_font(14, bold=True)
    f_row = _get_font(14)
    f_tot = _get_font(15, bold=True)

    d.rectangle([0, 0, width, 8], fill="#f59e0b")
    d.text((40, 24), "NHÀ THUỐC BỆNH VIỆN TRUNG ƯƠNG", fill="#78350f", font=f_title)
    d.text(
        (40, 58), "Phiếu thu tiền thuốc điều trị ngoại trú  ·  Mã số: BK-882190", fill="#64748b", font=f_sub
    )
    d.line([(40, 100), (width - 40, 100)], fill="#e2e8f0", width=2)
    d.text((width // 2 - 130, 115), "PHIẾU XUẤT THUỐC & BIÊN LAI", fill="#0f172a", font=f_title)

    y_hdr = 165
    d.rectangle([40, y_hdr - 6, width - 40, y_hdr + 28], fill="#f1f5f9", outline="#cbd5e1", width=1)
    d.text((50, y_hdr), "STT", fill="#334155", font=f_hdr)
    d.text((120, y_hdr), "Tên thuốc", fill="#334155", font=f_hdr)
    d.text((475, y_hdr), "SL", fill="#334155", font=f_hdr)
    d.text((560, y_hdr), "ĐVT", fill="#334155", font=f_hdr)
    d.text((650, y_hdr), "Đơn giá (VND)", fill="#334155", font=f_hdr)
    d.text((780, y_hdr), "Thành tiền (VND)", fill="#334155", font=f_hdr)

    # 4 rows printed on physical paper:
    paper_rows = [
        {
            "stt": 1,
            "ten_dich_vu": "Cefuroxim 250mg",
            "so_luong": 10,
            "don_vi_tinh": "Viên",
            "don_gia": 6500,
            "thanh_tien": 65000,
        },
        {
            "stt": 2,
            "ten_dich_vu": "Men vi sinh Entero",
            "so_luong": 10,
            "don_vi_tinh": "Gói",
            "don_gia": 4200,
            "thanh_tien": 42000,
        },
        {
            "stt": 3,
            "ten_dich_vu": "Paracetamol 500mg (MISSED BY OCR)",
            "so_luong": 10,
            "don_vi_tinh": "Viên",
            "don_gia": 1500,
            "thanh_tien": 15000,
        },
        {
            "stt": 4,
            "ten_dich_vu": "Vitamin B1 100mg",
            "so_luong": 30,
            "don_vi_tinh": "Viên",
            "don_gia": 500,
            "thanh_tien": 15000,
        },
    ]

    ocr_boxes = []
    items_out = []
    y = 210

    for idx, it in enumerate(paper_rows):
        row_y = y
        # Draw all 4 rows on the physical invoice image
        d.line([(40, row_y + 30), (width - 40, row_y + 30)], fill="#e2e8f0", width=1)
        d.text((60, row_y), str(it["stt"]), fill="#1e293b", font=f_row)
        d.text((120, row_y), it["ten_dich_vu"].replace(" (MISSED BY OCR)", ""), fill="#1e293b", font=f_row)
        d.text((485, row_y), str(it["so_luong"]), fill="#1e293b", font=f_row)
        d.text((565, row_y), it["don_vi_tinh"], fill="#1e293b", font=f_row)
        d.text((660, row_y), f"{it['don_gia']:,}", fill="#1e293b", font=f_row)
        d.text((795, row_y), f"{it['thanh_tien']:,}", fill="#1e293b", font=f_row)

        # BUT OCR dropped Row 3! (Only rows 1, 2, 4 are in extracted items)
        if it["stt"] != 3:
            b_stt = [50, row_y - 3, 80, row_y + 24]
            b_name = [115, row_y - 3, 430, row_y + 24]
            b_qty = [475, row_y - 3, 510, row_y + 24]
            b_unit = [555, row_y - 3, 605, row_y + 24]
            b_price = [650, row_y - 3, 730, row_y + 24]
            b_amt = [785, row_y - 3, 885, row_y + 24]

            id_stt = len(ocr_boxes)
            ocr_boxes.append(b_stt)
            id_name = len(ocr_boxes)
            ocr_boxes.append(b_name)
            id_qty = len(ocr_boxes)
            ocr_boxes.append(b_qty)
            id_unit = len(ocr_boxes)
            ocr_boxes.append(b_unit)
            id_price = len(ocr_boxes)
            ocr_boxes.append(b_price)
            id_amt = len(ocr_boxes)
            ocr_boxes.append(b_amt)

            items_out.append(
                {
                    "stt": it["stt"],
                    "ten_dich_vu": it["ten_dich_vu"],
                    "so_luong": it["so_luong"],
                    "don_vi_tinh": it["don_vi_tinh"],
                    "don_gia": it["don_gia"],
                    "thanh_tien": it["thanh_tien"],
                    "evidence_box_ids": {
                        "stt": [id_stt],
                        "ten_dich_vu": [id_name],
                        "so_luong": [id_qty],
                        "don_vi_tinh": [id_unit],
                        "don_gia": [id_price],
                        "thanh_tien": [id_amt],
                    },
                }
            )
        y += 42

    printed_total = 137000  # Total printed on receipt
    extracted_sum = sum(it["thanh_tien"] for it in items_out)  # 122,000 (missing 15,000)

    d.rectangle([40, y + 8, width - 40, y + 48], fill="#fff7ed", outline="#fed7aa", width=1)
    d.text((120, y + 16), "TỔNG CỘNG TIỀN PHẢI TRẢ:", fill="#9a3412", font=f_tot)
    d.text((770, y + 16), f"{printed_total:,} VND", fill="#9a3412", font=f_tot)

    box_total = [760, y + 12, 900, y + 42]
    id_tot = len(ocr_boxes)
    ocr_boxes.append(box_total)

    out = io.BytesIO()
    im.save(out, format="PNG")
    png_bytes = out.getvalue()

    result = {
        "document_type": "MEDICINE_INVOICE",
        "status": "EXTRACTED",
        "qa_status": "BLOCKED_TOTAL_MISMATCH",
        "ready_for_rpa": False,
        "image_size": [width, height],
        "ocr_boxes": ocr_boxes,
        "document_total": {"value": printed_total, "box_id": id_tot},
        "total_checks": [
            {
                "field": "thanh_tien",
                "document_total": printed_total,
                "rows_sum": extracted_sum,
                "difference": extracted_sum - printed_total,  # -15000
                "status": "MISMATCH",
            }
        ],
        "items": items_out,
    }
    return png_bytes, result


def generate_payment_sample() -> tuple[bytes, dict[str, Any]]:
    """Generate hospital payment receipt with Vietnamese BHYT insurance split."""
    width, height = 960, 520
    im = Image.new("RGB", (width, height), "#ffffff")
    d = ImageDraw.Draw(im)

    f_title = _get_font(21, bold=True)
    f_sub = _get_font(13)
    f_hdr = _get_font(13, bold=True)
    f_row = _get_font(13)
    f_tot = _get_font(14, bold=True)

    d.rectangle([0, 0, width, 8], fill="#10b981")
    d.text((40, 24), "BỆNH VIỆN ĐA KHOA TỈNH  ·  KHOA KHÁM BỆNH", fill="#065f46", font=f_title)
    d.text((40, 58), "BẢNG KÊ CHI PHÍ KHÁM BỆNH, CHỮA BỆNH NGOẠI TRÚ (BHYT)", fill="#047857", font=f_hdr)
    d.text((40, 80), "Bệnh nhân: NGUYỄN VĂN A  ·  Mã thẻ BHYT: DN4790123456789", fill="#64748b", font=f_sub)
    d.line([(40, 105), (width - 40, 105)], fill="#e2e8f0", width=2)

    y_hdr = 145
    d.rectangle([40, y_hdr - 6, width - 40, y_hdr + 28], fill="#f0fdf4", outline="#bbf7d0", width=1)
    d.text((48, y_hdr), "STT", fill="#166534", font=f_hdr)
    d.text((100, y_hdr), "Nội dung dịch vụ kỹ thuật", fill="#166534", font=f_hdr)
    d.text((430, y_hdr), "SL", fill="#166534", font=f_hdr)
    d.text((475, y_hdr), "Tổng chi phí", fill="#166534", font=f_hdr)
    d.text((610, y_hdr), "BHYT chi trả", fill="#166534", font=f_hdr)
    d.text((750, y_hdr), "BN thanh toán", fill="#166534", font=f_hdr)

    pay_items = [
        {
            "stt": 1,
            "ten_dich_vu": "Khám chuyên khoa Nội",
            "so_luong": 1,
            "don_vi_tinh": "Lần",
            "don_gia": 150000,
            "thanh_tien": 150000,
            "chi_phi": 150000,
            "bhyt_chi": 120000,
            "so_giam": 0,
            "benh_nhan_thanh_toan": 30000,
        },
        {
            "stt": 2,
            "ten_dich_vu": "Chụp X-quang ngực thẳng",
            "so_luong": 1,
            "don_vi_tinh": "Lần",
            "don_gia": 180000,
            "thanh_tien": 180000,
            "chi_phi": 180000,
            "bhyt_chi": 144000,
            "so_giam": 0,
            "benh_nhan_thanh_toan": 36000,
        },
        {
            "stt": 3,
            "ten_dich_vu": "Xét nghiệm công thức máu toàn phần",
            "so_luong": 1,
            "don_vi_tinh": "Lần",
            "don_gia": 120000,
            "thanh_tien": 120000,
            "chi_phi": 120000,
            "bhyt_chi": 96000,
            "so_giam": 0,
            "benh_nhan_thanh_toan": 24000,
        },
    ]

    ocr_boxes = []
    items_out = []
    y = 190

    for idx, it in enumerate(pay_items):
        row_y = y
        d.line([(40, row_y + 30), (width - 40, row_y + 30)], fill="#e2e8f0", width=1)
        d.text((55, row_y), str(it["stt"]), fill="#1e293b", font=f_row)
        d.text((100, row_y), it["ten_dich_vu"], fill="#1e293b", font=f_row)
        d.text((435, row_y), str(it["so_luong"]), fill="#1e293b", font=f_row)
        d.text((485, row_y), f"{it['chi_phi']:,}", fill="#1e293b", font=f_row)
        d.text((625, row_y), f"{it['bhyt_chi']:,}", fill="#047857", font=f_row)
        d.text((765, row_y), f"{it['benh_nhan_thanh_toan']:,}", fill="#b91c1c", font=f_row)

        b_stt = [45, row_y - 3, 75, row_y + 24]
        b_name = [95, row_y - 3, 400, row_y + 24]
        b_qty = [430, row_y - 3, 455, row_y + 24]
        b_unit = [455, row_y - 3, 470, row_y + 24]
        b_cost = [480, row_y - 3, 580, row_y + 24]
        b_ins = [615, row_y - 3, 715, row_y + 24]
        b_pat = [755, row_y - 3, 875, row_y + 24]

        id_stt = len(ocr_boxes)
        ocr_boxes.append(b_stt)
        id_name = len(ocr_boxes)
        ocr_boxes.append(b_name)
        id_qty = len(ocr_boxes)
        ocr_boxes.append(b_qty)
        id_unit = len(ocr_boxes)
        ocr_boxes.append(b_unit)
        id_cost = len(ocr_boxes)
        ocr_boxes.append(b_cost)
        id_ins = len(ocr_boxes)
        ocr_boxes.append(b_ins)
        id_pat = len(ocr_boxes)
        ocr_boxes.append(b_pat)

        items_out.append(
            {
                "stt": it["stt"],
                "ten_dich_vu": it["ten_dich_vu"],
                "so_luong": it["so_luong"],
                "don_vi_tinh": it["don_vi_tinh"],
                "don_gia": it["don_gia"],
                "thanh_tien": it["thanh_tien"],
                "payment_details": {
                    "chi_phi": it["chi_phi"],
                    "bhyt_chi": it["bhyt_chi"],
                    "so_giam": it["so_giam"],
                    "benh_nhan_thanh_toan": it["benh_nhan_thanh_toan"],
                },
                "evidence_box_ids": {
                    "stt": [id_stt],
                    "ten_dich_vu": [id_name],
                    "so_luong": [id_qty],
                    "don_vi_tinh": [id_unit],
                    "don_gia": [id_cost],
                    "thanh_tien": [id_cost],
                    "chi_phi": [id_cost],
                    "bhyt_chi": [id_ins],
                    "benh_nhan_thanh_toan": [id_pat],
                },
            }
        )
        y += 42

    total_cost = sum(it["chi_phi"] for it in pay_items)
    total_bhyt = sum(it["bhyt_chi"] for it in pay_items)
    total_pat = sum(it["benh_nhan_thanh_toan"] for it in pay_items)

    d.rectangle([40, y + 8, width - 40, y + 48], fill="#f0fdf4", outline="#bbf7d0", width=1)
    d.text((100, y + 16), "TỔNG THANH TOÁN (VND):", fill="#166534", font=f_tot)
    d.text((485, y + 16), f"{total_cost:,}", fill="#166534", font=f_tot)
    d.text((625, y + 16), f"{total_bhyt:,}", fill="#047857", font=f_tot)
    d.text((765, y + 16), f"{total_pat:,}", fill="#b91c1c", font=f_tot)

    box_total = [755, y + 12, 890, y + 42]
    id_tot = len(ocr_boxes)
    ocr_boxes.append(box_total)

    out = io.BytesIO()
    im.save(out, format="PNG")
    png_bytes = out.getvalue()

    result = {
        "document_type": "MEDICAL_PAYMENT",
        "status": "EXTRACTED",
        "qa_status": "PENDING_HUMAN_REVIEW",
        "ready_for_rpa": False,
        "image_size": [width, height],
        "ocr_boxes": ocr_boxes,
        "document_total": {"value": total_pat, "box_id": id_tot},
        "total_checks": [
            {
                "field": "benh_nhan_thanh_toan",
                "document_total": total_pat,
                "rows_sum": total_pat,
                "difference": 0,
                "status": "MATCH",
            }
        ],
        "items": items_out,
    }
    return png_bytes, result
