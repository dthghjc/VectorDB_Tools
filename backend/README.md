# uv 工作流指南 ⚡️

本文档为本项目后端开发的 `uv` 工作流指南。我们使用 `uv` 进行环境管理和依赖解析，旨在统一开发环境、保证构建的可复现性，并利用其无与-伦比的速度提升开发效率。

**锁定文件**: 本项目使用 `uv.lock` 作为唯一的依赖锁定文件，以确保最高的安全性和环境一致性。

---

### 1. 首次配置项目 (For Newcomers)

对于**首次**从代码库克隆本项目，并需要在本地从零开始配置环境的开发者，请**严格按顺序**执行以下所有步骤。

**步骤 1.1: 初始化项目配置文件 (如果需要)**
此命令会创建一个 `pyproject.toml` 文件，它是我们项目依赖的“设计蓝图”。
> **注意**: 如果项目中已经存在 `pyproject.toml` 文件，请跳过此步。
```bash
uv init
```

**步骤 1.2: 创建指定版本的虚拟环境**
为了保证团队环境绝对一致，我们强制使用指定的 Python 版本（例如 3.11）来创建虚拟环境。
```bash
# 首先，你可以通过 `uv python list` 查看 uv 在你系统上发现了哪些可用的 Python 版本。
# 然后，在创建环境时通过 `-p` 或 `--python` 参数指定版本：
uv venv -p 3.10
```
此命令将在当前目录下创建一个 `.venv` 文件夹，作为我们项目的隔离环境。

**步骤 1.3: 安装所有依赖**
此命令会读取 `pyproject.toml` 和 `uv.lock` 文件，并将所有锁定的依赖精确地安装到你刚刚创建的 `.venv` 中。
```bash
uv pip sync pyproject.toml
```
至此，你的本地开发环境已配置完毕，并与团队标准完全一致。

---

### 2. 日常开发工作流 (Daily Workflow)

在日常开发中，请使用以下 `uv` 命令来管理项目。

**核心理念**: 我们使用 `uv run` 来执行所有命令。这可以确保命令总是在正确的虚拟环境中运行，**因此无需手动运行 `source .venv/bin/activate`**。

| 任务 | 命令 |
| :--- | :--- |
| **运行开发服务器** | `uv run uvicorn main:app --reload` |
| **添加新依赖** | `uv add "package-name"` |
| **移除依赖** | `uv remove "package-name"` |
| **运行测试** | `uv run pytest` |
| **查看依赖树** | `uv tree` |
| **更新所有依赖** | 详见下方“维护与升级”部分 |

---

### 3. 维护与升级 (Maintenance & Upgrades)

**场景**:
1.  当你需要将所有现有依赖更新到最新的兼容版本时（例如，为了获取安全补丁或新功能）。
2.  当你手动修改了 `pyproject.toml` 文件中的版本约束，需要重新生成锁定文件时。

**工作流程**:

**步骤 3.1: 重新编译并锁定依赖**
此命令会检查 `pyproject.toml` 中的版本约束，查找最新的兼容包版本，然后生成或重写 `uv.lock` 文件。`--upgrade` 参数是关键。
```bash
uv pip compile pyproject.toml -o uv.lock --upgrade
```
> **重要**: 运行此命令后，你应该将更新后的 `uv.lock` 文件提交到 Git。它是保证团队环境一致性的核心。

**步骤 3.2: 将更新同步到本地环境**
在生成了新的 `uv.lock` 文件后，运行 `sync` 命令来将这些变更应用到你本地的 `.venv` 环境中。
```bash
uv pip sync
```

---
### 附录：命令解析

* `uv init`: 创建项目的“蓝图” (`pyproject.toml`)。
* `uv venv`: 准备一块“空地基” (`.venv`)。
* `uv add`: **功能驱动**。向“蓝图”中添加新工具，并被动更新“施工计划书” (`uv.lock`)。
* `uv pip compile`: **维护驱动**。主动重新规划，生成一份最新的“施工计划书” (`uv.lock`)。
* `uv pip sync pyproject.toml`: **执行驱动**。严格按照“施工计划书” (`uv.lock`) 来建造或改造“施工现场” (`.venv`)。
* `uv run`: **运行驱动**。在“施工现场” (`.venv`) 中安全地运行程序。

### 附录：uv pip sync pyproject.toml 的使用

- 场景 1：你正在积极开发，需要一个新功能

    你需要 email-validator 来验证邮箱。

    你应该用: uv add email-validator

    结果: email-validator 被添加到了 pyproject.toml，uv.lock 更新了，并且 email-validator 已经被安装好了。你不需要再运行 uv pip sync，可以直接在代码里 import 并使用它了。

- 场景 2：你刚从 Git 上拉取了同事的最新代码

    你的同事用 uv add 添加了一个新的库，然后把更新后的 pyproject.toml 和 uv.lock 推送到了 Git。

    你应该用: uv pip sync pyproject.toml

    结果: uv 会读取最新的 uv.lock 文件，发现里面有一个你的本地 .venv 环境里还没有的新库，于是把它安装进来。

- 场景 3：你感觉你的本地环境可能“不干净”了

    你可能为了调试，手动用 uv pip install 装了一些测试包，但没有用 uv add 把它们加到 pyproject.toml。

    你应该用: uv pip sync pyproject.toml

    结果: uv 会发现你手动安装的那些包不在 uv.lock 的“蓝图”里，于是会自动帮你把它们全部卸载掉，还你一个干净、可复现的环境。

# Alembic 数据库迁移指南 📦

本文档为本项目后端开发的官方数据库迁移工作流指南。我们使用 **Alembic** 来管理数据库结构 (Schema) 的所有变更，确保每一次修改都有记录、可追溯、可重复。

**核心理念**: 永远不要手动修改线上数据库！所有的结构变更都必须通过创建和执行 Alembic 迁移脚本来完成。

---

### 1. 首次配置 (One-Time Setup)

这部分描述了如何从零开始在项目中集成 Alembic。这是一个**一次性**的配置过程，如果你已经配置完成，可以跳过此部分。

**步骤 1.1: 初始化 Alembic**
在 `backend` 目录下，此命令会创建 `alembic` 目录和 `alembic.ini` 配置文件。
```bash
uv run alembic init alembic
```

**步骤 1.2: 配置 `alembic.ini`**
打开 `alembic.ini` 文件，找到 `sqlalchemy.url` 这一行，并**将其用 `#` 注释掉或直接删除**。我们将从代码中动态加载此配置。

**步骤 1.3: 配置 `alembic/env.py`**
这是最关键的配置，目的是让 Alembic 能连接到正确的数据库，并找到你的 SQLAlchemy 模型。
1.  **导入模块**: 在文件顶部添加 `from app.core.config import settings` 和 `from app.models import Base`。
2.  **设置 `target_metadata`**: 找到 `target_metadata = None` 并修改为 `target_metadata = Base.metadata`。
3.  **配置数据库 URL**: 将 `run_migrations_online` 函数中的 URL 配置部分，修改为从 `settings` 对象获取：
    ```python
    # in run_migrations_online()
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    ```
> (注：详细的 `env.py` 完整代码请参考我们之前的讨论记录。)

---

### 2. 日常开发工作流 (Daily Workflow)

这是你每次需要修改数据库结构时（例如，添加一张新表、给现有表增加一个字段）都需要遵循的**三步流程**。

#### **步骤 2.1: 修改 SQLAlchemy 模型**

在你的 Python 代码中直接修改模型。Alembic 会将你的模型代码视为“最终目标状态”。

* **新增表**: 在 `app/models/` 目录下创建一个新的模型文件（如 `post.py`），并记得在 `app/models/__init__.py` 中导入它。
* **修改表**: 在已有的模型文件（如 `app/models/user.py`）中添加、删除或修改列 (`mapped_column`)。
* **删除表**: 在 `app/models/__init__.py` 中移除该模型的导入，并可以删除对应的模型文件。

**示例：给 User 模型添加 `nickname` 字段**
```python
# backend/app/models/user.py

class User(Base, TimestampMixin):
    # ... (其他字段)
    nickname: Mapped[str | None] = mapped_column(String(50)) # <-- 新增的字段
```

#### **步骤 2.2: 自动生成迁移脚本**

修改完模型后，运行 `revision` 命令。Alembic 会自动比较你的模型（目标状态）和当前数据库（实际状态）的差异，并生成一个迁移脚本。

```bash
uv run alembic revision --autogenerate -m "Add nickname to User model"
```
* `--autogenerate`: 开启自动检测功能。
* `-m "..."`: 为本次迁移写一句清晰的描述，说明你做了什么。**请务必认真填写！**

> **检查**: 命令成功后，请打开 `alembic/versions/` 目录下新生成的 Python 文件，**大致检查一下**里面的 `upgrade()` 和 `downgrade()` 函数是否符合你的预期。

#### **步骤 2.3: 应用迁移到数据库**

确认迁移脚本无误后，运行 `upgrade` 命令将变更应用到数据库。

```bash
uv run alembic upgrade head
```
* `head`: 表示应用所有迁移，直到最新版本。

命令执行成功后，你的数据库结构就和你的模型代码保持一致了。

---

### 3. 其他常用命令

| 任务 | 命令 | 描述 |
| :--- | :--- | :--- |
| **查看迁移历史** | `uv run alembic history` | 按顺序列出所有迁移及其版本号。 |
| **查看当前版本** | `uv run alembic current` | 显示数据库当前处于哪个迁移版本。 |
| **回滚一次迁移** | `uv run alembic downgrade -1` | 撤销最近一次的迁移。非常适合在本地开发中快速撤销错误操作。 |
| **升级到指定版本** | `uv run alembic upgrade <version_id>` | 将数据库升级到某个特定的历史版本。 |
| **降级到指定版本** | `uv run alembic downgrade <version_id>` | 将数据库降级到某个特定的历史版本。 |