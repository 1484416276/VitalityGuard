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
- 发布工作流增加产物存在性校验并修正路径分隔符

## 真实测试

```bash
python main.py --self-test --test-mode --dry-run
python main.py --self-test --test-mode --dry-run
```

## 运行验证规则

- **启动程序来验证功能时先杀掉旧进程**：防止旧进程占用文件或端口，确保测试的是最新代码。
  ```bash
  taskkill /F /IM VitalityGuard.exe
  ```

## 测试维护规则

- **本地测试用例维护**：
  - 所有功能的测试用例必须存放在本地 `tests/` 目录（已加入 `.gitignore`）。
  - 只有当对应功能被移除时，才清理相关的测试文件。
  - 每次修改代码后，必须维护并更新对应的测试用例。
  - **Push 前必测**：在 push 代码前，必须确保 `tests/` 目录下的所有测试用例通过。

- **真实测试与无打扰原则**：
  - 功能必须经过**真实测试**（Integration/Functional Test）验证通过才算完成。
  - 测试应尽可能**减少对用户的打扰**（例如：使用自动化脚本、独立的测试进程、模拟 UI 循环，而不是依赖用户手动操作）。

- **打包时自动清理**：
  - 打包 EXE 前，会自动的覆盖旧的 `dist/*.exe` 文件，无需询问用户是否删除，无法覆盖到话，自动删除不要这件事一直打扰用户。
  - 若删除失败（如权限不足），应先强制终止占用进程（`taskkill`），然后再删除。
