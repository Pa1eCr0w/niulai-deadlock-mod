# 蓝牛来 0.1.1：视角数据修复与复现

恢复16个根骨挂点的坐标与旋转；保留原有11条相机定义、499骨骨架、动画引用及全部美术。

## 输入与结果

- 基线VPK SHA256：`4effc28b4e9caceb92e6035c1db2e6fda42047241ac5168f860e2fb9d637a981`。先从本仓库上一版Release的ModManager ZIP中提取VPK。
- 结果VPK SHA256：`497002a55ab2f582351005508616f1fa77f55276cfb74a057c78c7f3de52d203`，共26项资源。
- 未改动的原有资源：25项；哈希清单位于 `release-data/v0.1.1/payload-sha256.json`。
- `compiled/`增量资源、零售模型参考输入与修复代码均随本提交提供；不依赖个人设备路径、远程登录或安装状态。

## 确定性重新打包

```sh
python3 tools/camera-contract/rebuild.py BASELINE.vpk rebuilt.vpk --version 0.1.1
```

## 从修复源码重新生成

需要Python3、.NET10及ValveResourceFormat。上游仓库 `https://github.com/ValveResourceFormat/ValveResourceFormat`，本次读取器基于提交 `d9926fcb7df821b8476f4750250d5dbf61a6bab7`，先在该仓库应用 `tools/camera-contract/vrf-kv3-compat.patch`（KV3类型26/27兼容；上游许可证适用）。

```sh
python3 tools/camera-contract/rebuild.py BASELINE.vpk rebuilt-source.vpk --version 0.1.1 --from-source --vrf-project /path/to/ValveResourceFormat/ValveResourceFormat.csproj
```

`--dotnet`可指定dotnet可执行文件。脚本使用临时目录，并拒绝覆盖已有输出；逐资源验证后再断言完整VPK哈希。此源码路径已在本次发布环境执行，结果与群包/安装VPK字节一致；不声称已在干净机器完成整个历史模型作者工程构建。

## 检查边界

相机定义与各自当前零售模型一致，所有MDAT根挂点精确匹配；模型其他数据、材质和外观不改。499个骨骼与当前零售匹配，不覆盖游戏动作、运行时骨架或动画图。

完整验证摘要：`release-data/v0.1.1/validation.json`。实际安装哈希已核对；尚未完成所有技能/特殊状态的实机回归。

旧Release资产不改；奶蛋四肢分支保留。
