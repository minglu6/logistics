# 距离填充 Skill 使用指南

## 快速开始

在Claude Code中输入：

```
/distance-fill
```

这将自动处理江西仓的对账单，从可复用距离JSON中查找距离并填充。

## 使用方法

### 1. 默认处理江西仓

```
/distance-fill
```

或

```
/distance-fill jiangxi
```

### 2. 处理合肥仓

```
/distance-fill hefei
```

### 3. 指定具体文件

```
/distance-fill "data/jiangxi/summary/惠宜选江西仓1月份对账单.xlsx" "data/jiangxi/cache/reusable_distances.json"
```

### 4. 完整参数（包含起点）

```
/distance-fill "excel路径" "json路径" "起点名称"
```

## 距离查找规则

按照物流规则，距离按路线顺序查找：

1. **第一站距离** = 固定起点 -> 第一站
2. **后续站点距离** = 前一站 -> 当前站

### 仓库配置

| 仓库 | 固定起点 | 距离数据文件 |
|------|----------|--------------|
| 江西仓 | 惠宜选南昌仓 | data/jiangxi/cache/reusable_distances.json |
| 合肥仓 | 丰树合肥现代综合产业园 | data/hefei/cache/reusable_distances.json |

## 输出格式

处理后的店名列格式：

```
店名1-距离1km
店名2-距离2km
店名3-?km
```

- 找到的距离显示具体数值
- 未找到的距离标记为 `?km`

## 输出文件

结果保存到新文件，不会覆盖原文件：
- 输入：`惠宜选江西仓1月份对账单.xlsx`
- 输出：`惠宜选江西仓1月份对账单_filled.xlsx`

## 处理报告

运行后会显示详细报告：

```
处理完成!
  总路线数: 23
  总站点数: 147
  找到距离: 116 (78.9%)
  未找到距离: 31 (21.1%)

未找到的距离段:
  行2: 共橙一站式超市（南昌小洲路店） -> 共橙一站式超市（兴国县将军大道店）
  ...
```

## 智能匹配

Skill会自动处理以下格式差异：

1. **括号格式**：`（）` 和 `()` 通用
2. **品牌名称**：`历臣` 和 `厉臣` 通用
3. **店名格式**：`共橙一站式` 和 `共橙-站式` 通用

## 补充未找到的距离

1. 查看报告中"未找到的距离段"
2. 手动查询这些距离
3. 添加到JSON文件中，格式为：
   ```json
   {
     "起点 -> 终点": 距离
   }
   ```
4. 重新运行 `/distance-fill`

## Skill位置

```
C:\Users\luming2\.claude\skills\distance-fill\
├── skill.json          # Skill配置
├── run.py              # 入口脚本
├── fill_distances.py   # 核心逻辑
└── README.md           # 说明文档
```

## 故障排除

### 找不到对账单文件
- 确认文件名格式：`惠宜选*仓*月*对账单*.xlsx`
- 确认文件位置：`data/仓库名/summary/` 目录下

### 找不到距离JSON文件
- 确认文件存在：`data/仓库名/cache/reusable_distances.json`

### 匹配率低
- 检查店名格式是否一致
- 查看未匹配的距离段，手动补充到JSON

## 相关命令

- `/logistics-fill` - 填充每日物流数据到对账单
- `/distance-fill` - 填充可复用距离数据
