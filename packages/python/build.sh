#!/bin/bash
#
# E2B MCP Server - 打包脚本
# 自动化构建 Python 包
#

set -e  # 遇到错误立即退出

echo "================================"
echo "E2B MCP Server - 打包工具"
echo "================================"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 Poetry
echo "📦 检查构建工具..."
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}⚠️  Poetry 未安装${NC}"
    echo ""
    echo "请选择安装方式："
    echo "  1. pip install poetry"
    echo "  2. curl -sSL https://install.python-poetry.org | python3 -"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} Poetry 已安装: $(poetry --version)"
echo ""

# 显示当前版本
CURRENT_VERSION=$(grep "^version = " pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "📌 当前版本: ${CURRENT_VERSION}"
echo ""

# 询问是否更新版本
read -p "是否更新版本? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "选择版本更新类型:"
    echo "  1. patch  (补丁版本, 例如: 0.1.1 -> 0.1.2)"
    echo "  2. minor  (次版本, 例如: 0.1.1 -> 0.2.0)"
    echo "  3. major  (主版本, 例如: 0.1.1 -> 1.0.0)"
    echo "  4. custom (自定义版本)"
    echo ""
    read -p "请选择 (1-4): " -n 1 -r VERSION_TYPE
    echo ""
    
    case $VERSION_TYPE in
        1)
            poetry version patch
            ;;
        2)
            poetry version minor
            ;;
        3)
            poetry version major
            ;;
        4)
            read -p "输入新版本号: " NEW_VERSION
            poetry version $NEW_VERSION
            ;;
        *)
            echo -e "${RED}✗${NC} 无效选择"
            exit 1
            ;;
    esac
    
    NEW_VERSION=$(grep "^version = " pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    echo -e "${GREEN}✓${NC} 版本已更新: ${CURRENT_VERSION} -> ${NEW_VERSION}"
    echo ""
fi

# 清理旧构建
echo "🧹 清理旧构建..."
rm -rf dist/ build/ *.egg-info
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✓${NC} 清理完成"
echo ""

# 验证代码
echo "🔍 验证代码..."
if python3 -m py_compile e2b_mcp_server/*.py; then
    echo -e "${GREEN}✓${NC} 语法检查通过"
else
    echo -e "${RED}✗${NC} 语法检查失败"
    exit 1
fi
echo ""

# 安装依赖
echo "📥 安装依赖..."
poetry install --no-interaction
echo -e "${GREEN}✓${NC} 依赖安装完成"
echo ""

# 构建包
echo "🔨 开始构建..."
poetry build

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓${NC} 构建成功!"
    echo ""
    echo "📦 生成的文件:"
    ls -lh dist/
    echo ""
    
    # 显示构建信息
    WHEEL_FILE=$(ls dist/*.whl 2>/dev/null)
    TAR_FILE=$(ls dist/*.tar.gz 2>/dev/null)
    
    if [ -n "$WHEEL_FILE" ]; then
        WHEEL_SIZE=$(du -h "$WHEEL_FILE" | cut -f1)
        echo "  🎯 Wheel:  $(basename $WHEEL_FILE) ($WHEEL_SIZE)"
    fi
    
    if [ -n "$TAR_FILE" ]; then
        TAR_SIZE=$(du -h "$TAR_FILE" | cut -f1)
        echo "  📄 Source: $(basename $TAR_FILE) ($TAR_SIZE)"
    fi
    
    echo ""
    echo "================================"
    echo "✨ 打包完成!"
    echo "================================"
    echo ""
    echo "下一步操作:"
    echo "  • 本地测试: pip install dist/*.whl"
    echo "  • 发布测试: poetry publish -r testpypi"
    echo "  • 正式发布: poetry publish"
    echo ""
else
    echo -e "${RED}✗${NC} 构建失败"
    exit 1
fi
