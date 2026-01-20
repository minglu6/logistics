# 物流数据填充 Skill 使用指南

## 快速开始

Skill已经安装在你的系统中，可以直接在Claude Code中使用。

## 基本用法

### 1. 在物流数据目录中使用

进入包含临努*.xlsx文件的目录，然后在Claude Code中输入：

```
/logistics-fill
```

这将：
- 自动扫描当前目录所有 `临努*.xlsx` 文件
- 自动查找对账单文件
- 按日期顺序填充所有数据

### 2. 处理指定日期

```
/logistics-fill 1.9
```

只处理1月9日的数据。

### 3. 处理日期范围

```
/logistics-fill 1.9-1.15
```

处理1月9日到1月15日的所有数据。

## 注意事项

1. 确保文件名格式正确：`临努X.X.xlsx`
2. 确保对账单文件存在于同一目录
3. Skill会自动从最后一行继续填充，不会覆盖已有数据
4. 每次执行后会显示填充报告

## 工作流程示例

假设你有以下文件：
```
D:\Work\logistics\
  ├── 临努1.9.xlsx
  ├── 临努1.10.xlsx
  ├── 临努1.11.xlsx
  └── 惠宜选合肥仓1月份对账单.xlsx
```

在Claude Code中：
```
cd D:\Work\logistics
/logistics-fill 1.9-1.11
```

Skill会自动：
1. 读取临努1.9.xlsx、1.10.xlsx、1.11.xlsx
2. 识别每个文件中的车次和店铺
3. 填充到对账单文件
4. 显示填充报告

## 输出示例

```
目标文件: D:\Work\logistics\惠宜选合肥仓1月份对账单.xlsx
最后已填充行: 31
开始填充行: 32
================================================================================

处理: 1月9日 - 临努1.9.xlsx
  识别到 5 车数据
    第1车：6个店 -> 填充到第32行
    第2车：5个店 -> 填充到第33行
    ...

================================================================================

数据填充完成！
  处理文件数: 3
  添加车次数: 15
  总店铺数: 75
  数据填充到第 46 行
```

## 故障排除

### 如果Skill没有响应
1. 确认Skill已正确安装：检查 `~/.claude/skills/logistics-fill/` 目录
2. 重启Claude Code
3. 确保pandas和openpyxl已安装

### 如果找不到文件
- 使用绝对路径指定源目录和目标文件：
  ```
  /logistics-fill "D:\Work\logistics" "D:\Work\logistics\惠宜选合肥仓1月份对账单.xlsx"
  ```

## 高级用法

### 指定完整路径

```
/logistics-fill "D:\Work\logistics" "D:\Work\logistics\惠宜选合肥仓1月份对账单.xlsx" 1.9-1.15
```

参数说明：
- 第1个参数：源文件目录
- 第2个参数：目标对账单文件路径
- 第3个参数（可选）：日期范围

## 技巧

1. **批量处理**：一次处理整个月的数据
   ```
   /logistics-fill 1.1-1.31
   ```

2. **增量更新**：只处理新增的日期
   ```
   /logistics-fill 1.9
   ```

3. **验证数据**：填充后检查最后几行
   可以手动运行验证脚本或打开Excel文件查看

## 获取帮助

在Claude Code中询问：
- "如何使用logistics-fill skill？"
- "logistics-fill的参数是什么？"
- "为什么logistics-fill找不到文件？"

## Skill位置

Skill文件位于：`C:\Users\luming2\.claude\skills\logistics-fill\`

包含的文件：
- `skill.json` - Skill配置
- `run.py` - 入口脚本
- `fill_logistics_data.py` - 主要逻辑
- `README.md` - 详细文档
