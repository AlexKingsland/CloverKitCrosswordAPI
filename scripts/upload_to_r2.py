"""
Upload crossword puzzle JSON files to Cloudflare R2 storage.

This script uploads generated puzzle files to R2 bucket with proper metadata.

Required environment variables:
    R2_ACCESS_KEY_ID: R2 API access key
    R2_SECRET_ACCESS_KEY: R2 API secret key
    R2_ENDPOINT: R2 S3-compatible endpoint URL
    R2_BUCKET: R2 bucket name (default: crossword)

Usage:
    python scripts/upload_to_r2.py
    python scripts/upload_to_r2.py --input-dir out
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Tuple

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("❌ Error: boto3 is not installed")
    print("Install it with: pip install boto3")
    sys.exit(1)


def get_r2_client():
    """Create and return an S3 client configured for Cloudflare R2."""
    # Get credentials from environment
    access_key = os.getenv('R2_ACCESS_KEY_ID')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
    endpoint = os.getenv('R2_ENDPOINT')
    
    if not all([access_key, secret_key, endpoint]):
        print("❌ Missing required environment variables:")
        if not access_key:
            print("   - R2_ACCESS_KEY_ID")
        if not secret_key:
            print("   - R2_SECRET_ACCESS_KEY")
        if not endpoint:
            print("   - R2_ENDPOINT")
        print()
        print("Example:")
        print("  export R2_ACCESS_KEY_ID=your_access_key_id")
        print("  export R2_SECRET_ACCESS_KEY=your_secret_access_key")
        print("  export R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com")
        sys.exit(1)
    
    # Create S3 client for R2
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='auto'  # R2 uses 'auto' for region
    )
    
    return s3_client


def find_json_files(input_dir: Path) -> List[Tuple[Path, str]]:
    """
    Find all JSON files in the input directory and determine their R2 keys.
    
    Returns:
        List of tuples: (local_file_path, r2_key)
    """
    files = []
    
    # Look for files in the v1/generic structure
    base_path = input_dir / 'v1' / 'generic'
    
    if not base_path.exists():
        print(f"❌ Directory not found: {base_path}")
        print(f"   Make sure you've run generate_crosswords.py first")
        return files
    
    # Find all JSON files
    for json_file in base_path.rglob('*.json'):
        # Get the relative path from the input directory
        # This will be the R2 key
        relative_path = json_file.relative_to(input_dir)
        r2_key = str(relative_path).replace('\\', '/')  # Ensure forward slashes
        
        files.append((json_file, r2_key))
    
    return files


def upload_file_to_r2(s3_client, local_file: Path, bucket: str, key: str) -> bool:
    """
    Upload a single file to R2.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Upload with metadata
        s3_client.upload_file(
            str(local_file),
            bucket,
            key,
            ExtraArgs={
                'ContentType': 'application/json; charset=utf-8',
                'CacheControl': 'public, max-age=31536000, s-maxage=31536000, immutable',
            }
        )
        return True
    except ClientError as e:
        print(f"   ❌ Error uploading {key}: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error uploading {key}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Upload crossword puzzles to Cloudflare R2')
    parser.add_argument('--input-dir', default='out', help='Input directory containing generated files (default: out)')
    parser.add_argument('--bucket', default=None, help='R2 bucket name (default: from R2_BUCKET env var or "crossword")')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be uploaded without actually uploading')
    
    args = parser.parse_args()
    
    # Get bucket name
    bucket = args.bucket or os.getenv('R2_BUCKET', 'crossword')
    
    print("🚀 Cloudflare R2 Upload Tool")
    print(f"📦 Bucket: {bucket}")
    print(f"📁 Input directory: {args.input_dir}")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be uploaded")
    print()
    
    # Find all JSON files
    input_path = Path(args.input_dir)
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_path}")
        print("   Run generate_crosswords.py first to generate puzzle files")
        return 1
    
    files_to_upload = find_json_files(input_path)
    
    if not files_to_upload:
        print("❌ No JSON files found to upload")
        print(f"   Expected structure: {input_path}/v1/generic/[easy|medium|hard]/YYYY-MM-DD.json")
        return 1
    
    print(f"📋 Found {len(files_to_upload)} files to upload")
    print()
    
    if args.dry_run:
        print("Files that would be uploaded:")
        for local_file, r2_key in files_to_upload:
            file_size = local_file.stat().st_size
            print(f"  • {r2_key} ({file_size:,} bytes)")
        print()
        print("Run without --dry-run to upload these files")
        return 0
    
    # Create R2 client
    try:
        s3_client = get_r2_client()
    except Exception as e:
        print(f"❌ Failed to create R2 client: {e}")
        return 1
    
    # Verify bucket exists
    try:
        s3_client.head_bucket(Bucket=bucket)
        print(f"✓ Connected to bucket: {bucket}")
        print()
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ Bucket '{bucket}' not found")
            print("   Create the bucket in Cloudflare dashboard first")
        else:
            print(f"❌ Error accessing bucket: {e}")
        return 1
    
    # Upload files
    success_count = 0
    failed_count = 0
    
    for local_file, r2_key in files_to_upload:
        file_size = local_file.stat().st_size
        print(f"⬆️  Uploading: {r2_key} ({file_size:,} bytes)")
        
        if upload_file_to_r2(s3_client, local_file, bucket, r2_key):
            success_count += 1
            print(f"   ✓ Success")
        else:
            failed_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ Upload complete!")
    print(f"   Successful: {success_count}")
    if failed_count > 0:
        print(f"   Failed: {failed_count}")
    print()
    print("Next steps:")
    print(f"1. Verify files in R2 dashboard: https://dash.cloudflare.com/")
    print(f"2. Enable public access on the bucket if not already enabled")
    print(f"3. Test URL: https://YOUR-R2-HOST/{bucket}/v1/generic/medium/YYYY-MM-DD.json")
    print()
    
    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    exit(main())
