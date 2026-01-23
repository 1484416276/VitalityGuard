# 项目规则

## Lint

```bash
python -m ruff check .
```

## Typecheck

```bash
python -m mypy .
```

## 最近变更

- 清理未使用的导入与变量，确保 ruff 通过
- 更新 ruff 配置到 lint 分区并补充 mypy 配置
- 修复 winreg Optional 模块类型提示以通过 mypy

## 真实测试

```bash
python main.py --self-test --test-mode --dry-run
python main.py --self-test --test-mode --dry-run
```
