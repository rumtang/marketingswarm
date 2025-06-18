#!/usr/bin/env python3
"""
Export SQLite data for migration to Cloud SQL
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


def export_conversations(db_path: str = "test_marketing_swarm.db"):
    """Export all conversations from SQLite to JSON"""
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    try:
        # Connect to SQLite
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='conversations'")
        table_info = cursor.fetchone()
        if not table_info:
            print("❌ Conversations table not found")
            return
        
        print(f"Table schema:\n{table_info['sql']}\n")
        
        # Export conversations
        cursor.execute("SELECT * FROM conversations")
        conversations = [dict(row) for row in cursor.fetchall()]
        
        # Convert datetime strings if needed
        for conv in conversations:
            # Ensure datetime fields are strings
            for field in ['created_at', 'completed_at']:
                if conv.get(field) and not isinstance(conv[field], str):
                    conv[field] = str(conv[field])
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_count = cursor.fetchone()[0]
        
        # Save to JSON with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversations_export_{timestamp}.json"
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'source_database': db_path,
            'conversations': conversations,
            'total_count': total_count,
            'exported_count': len(conversations)
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Exported {len(conversations)} conversations to {filename}")
        print(f"   Total rows in database: {total_count}")
        
        # Show sample data
        if conversations:
            print("\nSample conversation:")
            sample = conversations[0]
            for key, value in sample.items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"  {key}: {value}")
        
        conn.close()
        return filename
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return None


def export_with_validation(db_path: str = "test_marketing_swarm.db"):
    """Export with additional validation and statistics"""
    
    filename = export_conversations(db_path)
    
    if filename and Path(filename).exists():
        # Validate the export
        with open(filename, 'r') as f:
            data = json.load(f)
        
        print("\n=== Export Validation ===")
        print(f"✓ File created: {filename}")
        print(f"✓ File size: {Path(filename).stat().st_size:,} bytes")
        print(f"✓ Conversations exported: {len(data['conversations'])}")
        
        # Check for any potential issues
        issues = []
        for i, conv in enumerate(data['conversations']):
            if not conv.get('id'):
                issues.append(f"Conversation {i} missing ID")
            if not conv.get('user_query'):
                issues.append(f"Conversation {conv.get('id', i)} missing user_query")
        
        if issues:
            print("\n⚠️  Potential issues found:")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"  - {issue}")
            if len(issues) > 5:
                print(f"  ... and {len(issues) - 5} more")
        else:
            print("✓ No data integrity issues found")
        
        return filename
    
    return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export SQLite data for Cloud SQL migration")
    parser.add_argument(
        "--db", 
        default="test_marketing_swarm.db",
        help="Path to SQLite database (default: test_marketing_swarm.db)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Perform additional validation on export"
    )
    
    args = parser.parse_args()
    
    print("=== Marketing Swarm SQLite Data Export ===\n")
    
    if args.validate:
        export_with_validation(args.db)
    else:
        export_conversations(args.db)