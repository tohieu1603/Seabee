"""
Dữ liệu mẫu cho hệ thống bán hải sản
Bán theo cân thực tế (kg/lạng)
"""

# ============================================
# DANH MỤC SẢN PHẨM
# ============================================

CATEGORIES = [
    {
        "name": "Tôm",
        "slug": "tom",
        "description": "Tôm các loại: tôm hùm, tôm sú, tôm thẻ...",
        "sort_order": 1
    },
    {
        "name": "Cua - Ghẹ",
        "slug": "cua-ghe",
        "description": "Cua hoàng đế, cua biển, ghẹ xanh...",
        "sort_order": 2
    },
    {
        "name": "Cá",
        "slug": "ca",
        "description": "Cá biển tươi sống, cá đông lạnh",
        "sort_order": 3
    },
    {
        "name": "Mực - Bạch tuộc",
        "slug": "muc-bach-tuoc",
        "description": "Mực ống, mực nang, bạch tuộc",
        "sort_order": 4
    },
    {
        "name": "Ốc - Sò - Nghêu",
        "slug": "oc-so-ngheu",
        "description": "Ốc hương, sò điệp, nghêu...",
        "sort_order": 5
    },
    {
        "name": "Hải sản khác",
        "slug": "hai-san-khac",
        "description": "Hàu, nhum biển, hải sâm...",
        "sort_order": 6
    },
]

# ============================================
# SẢN PHẨM HẢI SẢN
# ============================================

SEAFOOD_PRODUCTS = [
    # === TÔM ===
    {
        "code": "TOM-HUM-001",
        "name": "Tôm hùm Alaska",
        "category": "Tôm",
        "current_price": 2500000,  # 2.5 triệu/kg
        "stock_quantity": 15.5,
        "description": "Tôm hùm Alaska nhập khẩu, tươi sống, size lớn",
        "origin": "Alaska, Mỹ",
        "tags": ["cao cấp", "nhập khẩu", "tươi sống"]
    },
    {
        "code": "TOM-SU-001",
        "name": "Tôm sú biển",
        "category": "Tôm",
        "current_price": 450000,  # 450k/kg
        "stock_quantity": 50.0,
        "description": "Tôm sú biển Cà Mau, nuôi tự nhiên",
        "origin": "Cà Mau",
        "tags": ["tươi sống", "nuôi tự nhiên"]
    },
    {
        "code": "TOM-THE-001",
        "name": "Tôm thẻ",
        "category": "Tôm",
        "current_price": 250000,  # 250k/kg
        "stock_quantity": 30.0,
        "description": "Tôm thẻ tươi, size trung bình",
        "origin": "Bạc Liêu",
        "tags": ["tươi sống"]
    },

    # === CUA - GHẸ ===
    {
        "code": "CUA-HOANG-001",
        "name": "Cua hoàng đế Nga",
        "category": "Cua - Ghẹ",
        "current_price": 3500000,  # 3.5 triệu/kg
        "stock_quantity": 8.0,
        "description": "Cua hoàng đế Nga nhập khẩu, tươi sống, size khủng",
        "origin": "Nga",
        "tags": ["cao cấp", "nhập khẩu", "tươi sống"]
    },
    {
        "code": "CUA-BIEN-001",
        "name": "Cua biển",
        "category": "Cua - Ghẹ",
        "current_price": 600000,  # 600k/kg
        "stock_quantity": 25.0,
        "description": "Cua biển tươi sống, thịt chắc",
        "origin": "Phú Quốc",
        "tags": ["tươi sống"]
    },
    {
        "code": "GHE-XANH-001",
        "name": "Ghẹ xanh",
        "category": "Cua - Ghẹ",
        "current_price": 280000,  # 280k/kg
        "stock_quantity": 40.0,
        "description": "Ghẹ xanh biển, gạch đầy",
        "origin": "Phú Quốc",
        "tags": ["tươi sống"]
    },

    # === CÁ ===
    {
        "code": "CA-HOI-001",
        "name": "Cá hồi Nauy",
        "category": "Cá",
        "current_price": 450000,  # 450k/kg
        "stock_quantity": 60.0,
        "description": "Cá hồi Nauy nhập khẩu, phi lê hoặc nguyên con",
        "origin": "Nauy",
        "tags": ["nhập khẩu", "cao cấp", "sashimi"]
    },
    {
        "code": "CA-NGU-001",
        "name": "Cá ngừ đại dương",
        "category": "Cá",
        "current_price": 180000,  # 180k/kg
        "stock_quantity": 80.0,
        "description": "Cá ngừ vằn đại dương, thịt đỏ tươi",
        "origin": "Khánh Hòa",
        "tags": ["tươi nguyên"]
    },
    {
        "code": "CA-MU-001",
        "name": "Cá mú đỏ",
        "category": "Cá",
        "current_price": 350000,  # 350k/kg
        "stock_quantity": 45.0,
        "description": "Cá mú đỏ biển, thịt chắc ngọt",
        "origin": "Nha Trang",
        "tags": ["tươi sống", "cao cấp"]
    },
    {
        "code": "CA-DIEU-001",
        "name": "Cá điêu hồng",
        "category": "Cá",
        "current_price": 220000,  # 220k/kg
        "stock_quantity": 55.0,
        "description": "Cá điêu hồng tươi, thịt ngọt",
        "origin": "Vũng Tàu",
        "tags": ["tươi nguyên"]
    },

    # === MỰC - BẠCH TUỘC ===
    {
        "code": "MUC-ONG-001",
        "name": "Mực ống tươi",
        "category": "Mực - Bạch tuộc",
        "current_price": 150000,  # 150k/kg
        "stock_quantity": 35.0,
        "description": "Mực ống biển, tươi nguyên con",
        "origin": "Phan Thiết",
        "tags": ["tươi nguyên"]
    },
    {
        "code": "MUC-NANG-001",
        "name": "Mực nang",
        "category": "Mực - Bạch tuộc",
        "current_price": 180000,  # 180k/kg
        "stock_quantity": 28.0,
        "description": "Mực nang biển, thịt dày",
        "origin": "Phú Yên",
        "tags": ["tươi nguyên"]
    },
    {
        "code": "BACH-TUOC-001",
        "name": "Bạch tuộc",
        "category": "Mực - Bạch tuộc",
        "current_price": 220000,  # 220k/kg
        "stock_quantity": 20.0,
        "description": "Bạch tuộc biển, tươi sống",
        "origin": "Khánh Hòa",
        "tags": ["tươi sống"]
    },

    # === ỐC - SÒ - NGHÊU ===
    {
        "code": "OC-HUONG-001",
        "name": "Ốc hương",
        "category": "Ốc - Sò - Nghêu",
        "current_price": 280000,  # 280k/kg
        "stock_quantity": 25.0,
        "description": "Ốc hương biển, size to, thịt chắc",
        "origin": "Nha Trang",
        "tags": ["tươi sống"]
    },
    {
        "code": "SO-DIEP-001",
        "name": "Sò điệp",
        "category": "Ốc - Sò - Nghêu",
        "current_price": 120000,  # 120k/kg
        "stock_quantity": 40.0,
        "description": "Sò điệp biển, tươi sống",
        "origin": "Phú Quốc",
        "tags": ["tươi sống"]
    },
    {
        "code": "NGHEU-001",
        "name": "Nghêu",
        "category": "Ốc - Sò - Nghêu",
        "current_price": 45000,  # 45k/kg
        "stock_quantity": 60.0,
        "description": "Nghêu Bến Tre, tươi ngon",
        "origin": "Bến Tre",
        "tags": ["tươi sống"]
    },

    # === HẢI SẢN KHÁC ===
    {
        "code": "HAU-001",
        "name": "Hàu sữa",
        "category": "Hải sản khác",
        "current_price": 150000,  # 150k/kg
        "stock_quantity": 30.0,
        "description": "Hàu sữa tươi sống, béo ngậy",
        "origin": "Phú Quốc",
        "tags": ["tươi sống"]
    },
    {
        "code": "HAI-SAM-001",
        "name": "Hải sâm",
        "category": "Hải sản khác",
        "current_price": 1200000,  # 1.2 triệu/kg
        "stock_quantity": 5.0,
        "description": "Hải sâm Nhật Bản, cao cấp",
        "origin": "Nhật Bản",
        "tags": ["cao cấp", "nhập khẩu"]
    },
]

# ============================================
# NGUỒN NHẬP HÀNG
# ============================================

IMPORT_SOURCES = [
    {
        "name": "Anh Tuấn - Chợ Bình Điền",
        "source_type": "facebook",
        "contact_info": {
            "facebook_id": "tuanhaisan.binhdien",
            "phone": "0909123456",
            "facebook_url": "https://facebook.com/tuanhaisan"
        },
        "notes": "Nguồn chính cung cấp tôm cua"
    },
    {
        "name": "Chị Hoa - Zalo",
        "source_type": "zalo",
        "contact_info": {
            "zalo_id": "0912345678",
            "phone": "0912345678"
        },
        "notes": "Cung cấp tôm sú Cà Mau"
    },
    {
        "name": "Anh Minh - Messenger",
        "source_type": "messenger",
        "contact_info": {
            "messenger_id": "minhhaisanca",
            "phone": "0923456789"
        },
        "notes": "Nhập cá từ Nha Trang"
    },
    {
        "name": "Công ty TNHH Hải Sản Việt",
        "source_type": "company",
        "contact_info": {
            "phone": "0281234567",
            "email": "contact@haisanviet.com",
            "address": "123 Nguyễn Văn Linh, Q7, TP.HCM"
        },
        "notes": "Nhập khẩu hải sản cao cấp"
    },
    {
        "name": "Chợ hải sản Phú Quốc",
        "source_type": "market",
        "contact_info": {
            "phone": "0977123456",
            "address": "Chợ Dương Đông, Phú Quốc"
        },
        "notes": "Mua trực tiếp tại chợ"
    },
]

# ============================================
# LÔ NHẬP HÀNG MẪU
# ============================================

IMPORT_BATCHES = [
    {
        "seafood_code": "TOM-HUM-001",
        "batch_code": "IMP-20250121-001",
        "import_source": "Công ty TNHH Hải Sản Việt",
        "import_date": "2025-01-21",
        "import_price": 2200000,
        "sell_price": 2500000,
        "total_weight": 20.0,
        "remaining_weight": 15.5,
        "notes": "Lô tôm hùm Alaska nhập khẩu, chất lượng A",
        "import_details": {
            "container_no": "CONT2025001",
            "invoice_no": "INV-2025-001",
            "customs_cleared": True
        }
    },
    {
        "seafood_code": "TOM-SU-001",
        "batch_code": "IMP-20250120-001",
        "import_source": "Chị Hoa - Zalo",
        "import_date": "2025-01-20",
        "import_price": 380000,
        "sell_price": 450000,
        "total_weight": 100.0,
        "remaining_weight": 50.0,
        "notes": "Tôm sú Cà Mau, nuôi tự nhiên",
        "import_details": {
            "zalo_conversation": "https://zalo.me/conversation/123456",
            "payment_method": "Chuyển khoản"
        }
    },
    {
        "seafood_code": "CA-HOI-001",
        "batch_code": "IMP-20250119-001",
        "import_source": "Công ty TNHH Hải Sản Việt",
        "import_date": "2025-01-19",
        "import_price": 380000,
        "sell_price": 450000,
        "total_weight": 100.0,
        "remaining_weight": 60.0,
        "notes": "Cá hồi Nauy phi lê, đông lạnh",
        "import_details": {
            "origin_cert": "Norway Seafood Certificate"
        }
    },
    {
        "seafood_code": "CUA-HOANG-001",
        "batch_code": "IMP-20250118-001",
        "import_source": "Công ty TNHH Hải Sản Việt",
        "import_date": "2025-01-18",
        "import_price": 3200000,
        "sell_price": 3500000,
        "total_weight": 12.0,
        "remaining_weight": 8.0,
        "notes": "Cua hoàng đế Nga, tươi sống",
        "import_details": {
            "arrival_flight": "VN123"
        }
    },
    {
        "seafood_code": "GHE-XANH-001",
        "batch_code": "IMP-20250121-002",
        "import_source": "Chợ hải sản Phú Quốc",
        "import_date": "2025-01-21",
        "import_price": 250000,
        "sell_price": 280000,
        "total_weight": 50.0,
        "remaining_weight": 40.0,
        "notes": "Ghẹ xanh Phú Quốc, mua buổi sáng"
    },
]

# ============================================
# ĐƠN HÀNG MẪU
# ============================================

SAMPLE_ORDERS = [
    {
        "order_code": "POS-20250121-001",
        "customer_name": "Nguyễn Văn A",
        "customer_phone": "0901234567",
        "customer_address": "123 Nguyễn Huệ, Q1, TP.HCM",
        "payment_method": "cash",
        "payment_status": "paid",
        "status": "completed",
        "discount_amount": 0,
        "notes": "Giao hàng trước 6h chiều",
        "items": [
            {
                "seafood_code": "TOM-SU-001",
                "batch_code": "IMP-20250120-001",
                "weight": 3.5,  # 3.5 kg
                "unit_price": 450000,
                "notes": "Chọn con to"
            },
            {
                "seafood_code": "CA-HOI-001",
                "batch_code": "IMP-20250119-001",
                "weight": 2.0,  # 2 kg
                "unit_price": 450000,
                "notes": "Phi lê"
            },
            {
                "seafood_code": "NGHEU-001",
                "batch_code": None,
                "weight": 5.0,  # 5 kg
                "unit_price": 45000,
                "notes": ""
            }
        ]
    },
    {
        "order_code": "POS-20250121-002",
        "customer_name": "Trần Thị B",
        "customer_phone": "0912345678",
        "customer_address": "",
        "payment_method": "transfer",
        "payment_status": "paid",
        "status": "completed",
        "discount_amount": 0,
        "notes": "Khách quen",
        "items": [
            {
                "seafood_code": "TOM-HUM-001",
                "batch_code": "IMP-20250121-001",
                "weight": 1.5,  # 1.5 kg (1 con)
                "unit_price": 2500000,
                "notes": "Con 1.5kg cho tiệc"
            }
        ]
    },
    {
        "order_code": "POS-20250121-003",
        "customer_name": "Lê Văn C",
        "customer_phone": "0923456789",
        "customer_address": "456 Lê Lợi, Q1, TP.HCM",
        "payment_method": "momo",
        "payment_status": "paid",
        "status": "completed",
        "discount_amount": 50000,
        "notes": "",
        "items": [
            {
                "seafood_code": "CUA-HOANG-001",
                "batch_code": "IMP-20250118-001",
                "weight": 0.8,  # 800g
                "unit_price": 3500000,
                "notes": ""
            },
            {
                "seafood_code": "GHE-XANH-001",
                "batch_code": "IMP-20250121-002",
                "weight": 2.5,  # 2.5 kg
                "unit_price": 280000,
                "notes": "Chọn con béo"
            }
        ]
    },
]
