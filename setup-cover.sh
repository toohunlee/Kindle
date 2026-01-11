#!/bin/bash

echo "======================================================================"
echo "Kindle Cover Image Setup"
echo "======================================================================"
echo ""
echo "첨부하신 New York Times 이미지를 커버로 설정하려면:"
echo ""
echo "1. 이미지 파일을 이 폴더에 저장:"
echo "   /Users/seo/kindle-news-delivery/assets/"
echo ""
echo "2. 파일 이름을 다음 중 하나로 변경:"
echo "   - cover.jpg"
echo "   - cover.png"
echo ""
echo "예시 명령어:"
echo "   cp ~/Downloads/your-image.jpg assets/cover.jpg"
echo ""
echo "======================================================================"
echo ""

# Check if cover exists
if [ -f "assets/cover.jpg" ] || [ -f "assets/cover.png" ]; then
    echo "✅ 커버 이미지가 발견되었습니다!"
    ls -lh assets/cover.* 2>/dev/null
else
    echo "⚠️  커버 이미지가 아직 설정되지 않았습니다."
    echo ""
    echo "지금 설정하시겠습니까? (y/n)"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        echo ""
        echo "이미지 파일의 전체 경로를 입력하세요:"
        read -r image_path
        
        if [ -f "$image_path" ]; then
            # Detect file extension
            ext="${image_path##*.}"
            cp "$image_path" "assets/cover.$ext"
            echo "✅ 커버 이미지가 설정되었습니다: assets/cover.$ext"
        else
            echo "❌ 파일을 찾을 수 없습니다: $image_path"
        fi
    fi
fi

