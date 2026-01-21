# E2B MCP Server - 打包发布指南

## 📦 打包方式

这个 Python 项目使用 **Poetry** 进行依赖管理和打包。

## 🚀 快速打包

### 方法一：使用 Poetry（推荐）

```bash
# 1. 确保安装了 Poetry
pip install poetry

# 2. 安装依赖
poetry install

# 3. 构建包
poetry build

# 生成的文件在 dist/ 目录：
# - dist/e2b_mcp_server-0.1.1-py3-none-any.whl  (wheel 格式)
# - dist/e2b_mcp_server-0.1.1.tar.gz            (源码包)
```

### 方法二：使用 uv

```bash
# 1. 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 构建
uv build

# 生成的文件同样在 dist/ 目录
```

### 方法三：使用 pnpm（项目集成）

```bash
# 在项目根目录
pnpm run postPublish

# 这会执行：
# 1. poetry build
# 2. 准备发布到 PyPI
```

## 📋 打包前检查

### 1. 验证版本号

```bash
# 查看当前版本
poetry version

# 或查看 pyproject.toml
grep "version = " pyproject.toml
```

### 2. 更新版本（如需要）

```bash
# 补丁版本 (0.1.1 -> 0.1.2)
poetry version patch

# 次版本 (0.1.1 -> 0.2.0)
poetry version minor

# 主版本 (0.1.1 -> 1.0.0)
poetry version major

# 或直接指定版本
poetry version 0.2.0
```

### 3. 验证代码质量

```bash
# 语法检查
python3 -m py_compile e2b_mcp_server/*.py

# 运行测试（如果有）
pytest tests/

# 检查导入
python3 -c "from e2b_mcp_server import main; print('✓ Import OK')"
```

### 4. 清理旧构建

```bash
# 删除旧的构建文件
rm -rf dist/ build/ *.egg-info

# 清理 Python 缓存
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

## 🔨 完整打包流程

```bash
# 1. 进入项目目录
cd packages/python

# 2. 更新版本（可选）
poetry version patch

# 3. 清理旧构建
rm -rf dist/

# 4. 安装/更新依赖
poetry install

# 5. 构建包
poetry build

# 6. 验证构建结果
ls -lh dist/
```

## 📤 发布到 PyPI

### 发布到测试 PyPI（推荐先测试）

```bash
# 1. 配置测试 PyPI 仓库
poetry config repositories.testpypi https://test.pypi.org/legacy/

# 2. 配置测试 PyPI token
poetry config pypi-token.testpypi your-test-token-here

# 3. 发布到测试仓库
poetry publish -r testpypi

# 4. 测试安装
pip install --index-url https://test.pypi.org/simple/ e2b-mcp-server
```

### 发布到正式 PyPI

```bash
# 1. 配置 PyPI token
poetry config pypi-token.pypi your-token-here

# 2. 发布
poetry publish

# 或者一步到位（构建 + 发布）
poetry publish --build
```

### 使用环境变量发布

```bash
# 设置 token
export PYPI_TOKEN=your-token-here

# 发布
poetry config pypi-token.pypi ${PYPI_TOKEN}
poetry publish --skip-existing
```

## 🔍 验证已发布的包

```bash
# 从 PyPI 安装
pip install e2b-mcp-server

# 验证版本
pip show e2b-mcp-server

# 测试运行
python -m e2b_mcp_server --help
```

## 📁 打包文件说明

构建后 `dist/` 目录包含：

### Wheel 文件 (.whl)

```
e2b_mcp_server-0.1.1-py3-none-any.whl
```

- **py3**: 支持 Python 3
- **none**: 不依赖特定 ABI
- **any**: 支持所有平台

这是推荐的安装格式，安装速度快。

### 源码包 (.tar.gz)

```
e2b_mcp_server-0.1.1.tar.gz
```

包含完整源代码，用于：

- 需要从源码安装的场景
- 作为归档备份
- 审查代码

## 🛠️ 本地安装测试

### 从构建的包安装

```bash
# 安装 wheel
pip install dist/e2b_mcp_server-0.1.1-py3-none-any.whl

# 或安装源码包
pip install dist/e2b_mcp_server-0.1.1.tar.gz
```

### 开发模式安装

```bash
# 使用 poetry
poetry install

# 使用 pip（可编辑模式）
pip install -e .

# 这样修改代码后无需重新安装
```

## 📦 打包配置

### pyproject.toml 关键配置

```toml
[tool.poetry]
name = "e2b-mcp-server"              # PyPI 包名
version = "0.1.1"                    # 版本号
description = "E2B MCP Server"       # 简短描述
authors = ["e2b <hello@e2b.dev>"]   # 作者信息
license = "Apache-2.0"               # 许可证
readme = "README.md"                 # README 文件
packages = [{ include = "e2b_mcp_server" }]  # 包含的模块

[tool.poetry.dependencies]
python = ">=3.10,<4.0"              # Python 版本要求
# ... 其他依赖

[build-system]
requires = ["poetry-core"]           # 构建系统
build-backend = "poetry.core.masonry.api"
```

## 🔧 常见问题

### Q: 构建失败怎么办？

```bash
# 1. 更新 poetry
pip install --upgrade poetry

# 2. 清理缓存
poetry cache clear pypi --all

# 3. 重新安装依赖
rm poetry.lock
poetry install
```

### Q: 如何只构建 wheel？

```bash
poetry build -f wheel
```

### Q: 如何只构建源码包？

```bash
poetry build -f sdist
```

### Q: 打包时排除某些文件？

在 `pyproject.toml` 中添加：

```toml
[tool.poetry]
exclude = [
    "tests",
    "*.pyc",
    "__pycache__",
    "*.egg-info",
]
```

### Q: 如何查看包会包含哪些文件？

```bash
# 使用 poetry
poetry build -vvv

# 或者先打包，然后查看
tar -tzf dist/e2b_mcp_server-0.1.1.tar.gz
```

## 🎯 最佳实践

### 1. 版本管理

- 遵循 [语义化版本](https://semver.org/)
- 主版本：不兼容的 API 变更
- 次版本：向后兼容的功能新增
- 补丁版本：向后兼容的问题修正

### 2. 发布前清单

- [ ] 更新版本号
- [ ] 更新 CHANGELOG
- [ ] 运行所有测试
- [ ] 更新文档
- [ ] 构建并验证包
- [ ] 先发布到测试 PyPI
- [ ] 测试安装和运行
- [ ] 发布到正式 PyPI
- [ ] 创建 Git tag

### 3. 自动化发布

可以使用 GitHub Actions 自动化：

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install Poetry
        run: pip install poetry
      - name: Build and publish
        env:
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: |
          cd packages/python
          poetry config pypi-token.pypi ${PYPI_TOKEN}
          poetry publish --build
```

## 📚 相关资源

- [Poetry 文档](https://python-poetry.org/docs/)
- [PyPI 打包指南](https://packaging.python.org/)
- [语义化版本](https://semver.org/)
- [Python 打包用户指南](https://packaging.python.org/guides/)

## 💡 快速命令速查

```bash
# 构建
poetry build

# 发布到 PyPI
poetry publish

# 构建 + 发布
poetry publish --build

# 更新版本
poetry version patch

# 安装依赖
poetry install

# 清理构建
rm -rf dist/ build/ *.egg-info

# 本地测试安装
pip install dist/*.whl
```

---

有问题？查看 [Poetry 文档](https://python-poetry.org/docs/) 或提交 [Issue](https://github.com/yukkit/e2b-mcp-server/issues)
