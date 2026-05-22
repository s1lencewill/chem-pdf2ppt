"""
PDF转图片脚本 - 将PDF每一页转换为高清图片
PDF to Images Converter - Converts PDF pages to high-resolution images
"""
from pdf2image import convert_from_path
import os
import sys

def pdf_to_images(pdf_path, output_dir="pdf_images", dpi=200, fmt="PNG"):
    """
    将PDF转换为图片
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录
        dpi: 图片分辨率（越高越清晰，但文件越大）
        fmt: 输出格式（PNG, JPEG）
    """
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Converting PDF: {pdf_path}")
    print(f"Output directory: {output_dir}")
    print(f"DPI: {dpi}, Format: {fmt}")
    print("-" * 40)
    
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        print(f"Successfully converted {len(images)} pages")
        
        for i, image in enumerate(images):
            page_num = i + 1
            image_path = os.path.join(output_dir, f"page_{page_num}.{fmt.lower()}")
            image.save(image_path, fmt)
            print(f"  Saved: page_{page_num}.{fmt.lower()}")
        
        print("-" * 40)
        print(f"Conversion complete! {len(images)} pages saved to: {output_dir}")
        return len(images)
        
    except Exception as e:
        print(f"Error: {e}")
        return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_to_images.py <pdf_file> [output_dir] [dpi]")
        print("Examples:")
        print("  python convert_to_images.py paper.pdf")
        print("  python convert_to_images.py paper.pdf images 300")
        print("  python convert_to_images.py paper.pdf pages 150 jpg")
        return
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "pdf_images"
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    fmt = sys.argv[4].upper() if len(sys.argv) > 4 else "PNG"
    
    pdf_to_images(pdf_path, output_dir, dpi, fmt)

if __name__ == "__main__":
    main()
