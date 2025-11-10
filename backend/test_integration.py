#!/usr/bin/env python3
"""Quick integration test for meta_info_generator."""

import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, '/Users/jaeyoonmo/workspace/hwp-report-generator')

from app.models.template import Placeholder
from app.utils.meta_info_generator import create_meta_info_from_placeholders

def test_meta_info_generator():
    """Test meta_info_generator with sample data."""
    print("🧪 Testing meta_info_generator integration...")

    # Create sample placeholders
    placeholders = [
        Placeholder(
            id=1,
            template_id=1,
            placeholder_key="{{TITLE}}",
            created_at=datetime.now()
        ),
        Placeholder(
            id=2,
            template_id=1,
            placeholder_key="{{SUMMARY}}",
            created_at=datetime.now()
        ),
        Placeholder(
            id=3,
            template_id=1,
            placeholder_key="{{BACKGROUND}}",
            created_at=datetime.now()
        ),
        Placeholder(
            id=4,
            template_id=1,
            placeholder_key="{{CONCLUSION}}",
            created_at=datetime.now()
        ),
        Placeholder(
            id=5,
            template_id=1,
            placeholder_key="{{DATE}}",
            created_at=datetime.now()
        ),
        Placeholder(
            id=6,
            template_id=1,
            placeholder_key="{{RISK_ANALYSIS}}",  # Unknown keyword
            created_at=datetime.now()
        ),
    ]

    # Generate meta-info
    meta_info = create_meta_info_from_placeholders(placeholders)

    print(f"\n✅ Generated meta-info for {len(meta_info)} placeholders\n")

    # Verify structure
    for i, item in enumerate(meta_info, 1):
        print(f"[{i}] {item['key']}")
        print(f"    Type: {item['type']}")
        print(f"    Display Name: {item['display_name']}")
        print(f"    Required: {item['required']}")
        print(f"    Order Hint: {item['order_hint']}")
        print(f"    Description: {item['description'][:60]}...")
        print(f"    Examples: {item['examples']}")
        print()

    # Test assertions
    assert len(meta_info) == 6, f"Expected 6 items, got {len(meta_info)}"

    # Check TITLE
    title_item = meta_info[0]
    assert title_item["key"] == "{{TITLE}}"
    assert title_item["type"] == "section_title"
    assert title_item["display_name"] == "보고서 제목"
    assert title_item["required"] is True
    assert title_item["order_hint"] == 1
    print("✅ TITLE meta-info is correct")

    # Check DATE
    date_item = meta_info[4]
    assert date_item["key"] == "{{DATE}}"
    assert date_item["type"] == "metadata"
    assert date_item["display_name"] == "작성 날짜"
    assert date_item["required"] is False
    assert date_item["order_hint"] == 0
    print("✅ DATE meta-info is correct")

    # Check unknown keyword
    risk_item = meta_info[5]
    assert risk_item["key"] == "{{RISK_ANALYSIS}}"
    assert risk_item["type"] == "section_content"  # Default fallback
    assert risk_item["required"] is True
    assert risk_item["order_hint"] == 2
    print("✅ Unknown keyword RISK_ANALYSIS handled correctly")

    print("\n🎉 All integration tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_meta_info_generator()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
