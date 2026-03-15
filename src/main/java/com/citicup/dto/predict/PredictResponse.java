package com.citicup.dto.predict;

import lombok.Data;

@Data
public class PredictResponse {
    // 直接 JSON string/结构都行；这里先用 Object 占位
    private Object forecast;          // 预测路径/区间/点预测
    private Object extremeClass;      // 极端分类结果
    private Object explain;           // 可解释性信息（特征贡献/注意力等）
}