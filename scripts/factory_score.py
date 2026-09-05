#!/usr/bin/env python3
"""Phase 1 scoring table for the drawn pool pairs (seed = timestamp)."""
pairs = [
    ("《白痴》(陀思妥耶夫斯基) × 《美狄亚》(欧里庇得斯)",
     dict(结构咬合度=38, 爽文引擎潜力=29, 当代迁移度=19, 独特性=8), 94),
    ("《美狄亚》(欧里庇得斯) × 《双城记》(狄更斯)",
     dict(结构咬合度=36, 爽文引擎潜力=28, 当代迁移度=18, 独特性=8), 90),
    ("《浮士德》(歌德) × 《美狄亚》(欧里庇得斯)",
     dict(结构咬合度=34, 爽文引擎潜力=27, 当代迁移度=18, 独特性=7), 86),
    ("《白痴》(陀思妥耶夫斯基) × 《双城记》(狄更斯)",
     dict(结构咬合度=33, 爽文引擎潜力=25, 当代迁移度=17, 独特性=7), 82),
]
for name, subs, total in pairs:
    print(f"{name}: {sum(subs.values())} (结构{subs['结构咬合度']} 爽文{subs['爽文引擎潜力']} 迁移{subs['当代迁移度']} 独特{subs['独特性']}) → {'PASS' if total>=80 else 'FAIL'}")
