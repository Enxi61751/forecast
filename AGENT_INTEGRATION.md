# 智能体交互页面 - 前后端连接指南

## ✅ 前端配置已完成

### 1. 环境变量配置 (.env.local)
```env
VITE_API_MODE=auto                    # 自动模式：优先调用真实API，失败时回退mock
VITE_API_BASE_URL=http://localhost:8080  # Java后端地址（仅供其他服务使用）
VITE_API_TIMEOUT_MS=6000              # API超时时间
VITE_MOCK_RUN_OUTCOME=success         # Mock数据模式
```

### 2. Vite代理配置 (vite.config.ts)
```typescript
proxy: {
  "/api": {
    target: "http://localhost:8080",   # Java后端
    changeOrigin: true
  },
  "/agent": {
    target: "http://localhost:8001",   # Python智能体服务
    changeOrigin: true
  }
}
```

### 3. API端点
- 前端调用：`/agent/daily-feed`
- 最终转发：`http://localhost:8001/agent/daily-feed`

---

## 🔧 后端实现 (Python FastAPI)

### 需要添加以下内容到 `api.py`：

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# === 响应模型 ===
class AgentFeedItem(BaseModel):
    id: str
    agentName: str
    role: str
    direction: Optional[str] = None
    riskAttitude: Optional[str] = None
    rationale: Optional[str] = None
    confidence: Optional[float] = None
    memory: Optional[str] = None
    remark: Optional[str] = None
    updatedAt: Optional[str] = None
    tags: list[str] = []

class AgentFeedSection(BaseModel):
    id: str
    title: str
    items: list[AgentFeedItem] = []

class DailyReportResponse(BaseModel):
    asOf: Optional[str] = None
    reportTitle: Optional[str] = None
    reportBody: Optional[str] = None
    sections: list[AgentFeedSection] = []

class DailyReportRequest(BaseModel):
    simulation_input: Optional[SimulationInput] = Field(None, alias="input")
    current_price: float = 100.0
    current_volatility: float = 0.02
    dealer_inventory: int = 0
    max_position_limit: int = 500
    seed: int = 7
    steps: int = 5

# === API端点 ===
@app.post("/agent/daily-feed")
def get_agent_daily_feed(request: DailyReportRequest) -> dict:
    """生成代理日报"""
    try:
        # 运行模拟获取代理状态
        result = run_multi_step(
            simulation_input=request.simulation_input or SimulationInput(),
            current_price=request.current_price,
            current_volatility=request.current_volatility,
            dealer_inventory=request.dealer_inventory,
            steps=request.steps,
            max_position_limit=request.max_position_limit,
            seed=request.seed,
        )

        # 提取智能体状态
        agent_states = result.get("agent_states", {})
        
        # 构建代理日报项
        feed_items = []
        for agent_id, state in agent_states.items():
            state_dict = state.model_dump() if hasattr(state, "model_dump") else state
            
            item = AgentFeedItem(
                id=agent_id,
                agentName=state_dict.get("name", agent_id),
                role=state_dict.get("role", "Trader"),
                direction=state_dict.get("position_direction"),
                riskAttitude=state_dict.get("risk_attitude"),
                rationale=state_dict.get("reasoning"),
                confidence=state_dict.get("confidence_score"),
                updatedAt=datetime.utcnow().isoformat() + "Z",
                tags=["agent", "active"]
            )
            feed_items.append(item)

        # 如果无代理数据，返回示例
        if not feed_items:
            feed_items = [
                AgentFeedItem(
                    id="default-agent",
                    agentName="Market Agent",
                    role="Trader",
                    direction="NEUTRAL",
                    riskAttitude="MODERATE",
                    confidence=0.8,
                    updatedAt=datetime.utcnow().isoformat() + "Z",
                    tags=["simulation"]
                )
            ]

        sections = [
            AgentFeedSection(
                id="section-1",
                title="Agent Execution Summary",
                items=feed_items
            )
        ]

        report_body = f"""Agent Daily Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Market Snapshot:
  Current Price: {request.current_price}
  Volatility: {request.current_volatility:.2%}
  Simulation Steps: {request.steps}

Agent Activities:
{chr(10).join(f"- {item.agentName} ({item.role}): {item.direction or 'Neutral'}" for item in feed_items)}
"""

        response = DailyReportResponse(
            asOf=datetime.utcnow().isoformat() + "Z",
            reportTitle="Agent Daily Execution Report",
            reportBody=report_body,
            sections=sections
        )

        return {
            "code": 0,
            "data": response.model_dump(),
            "message": "Success"
        }
    
    except Exception as e:
        return {
            "code": -1,
            "data": None,
            "message": str(e)
        }
```

---

## 🚀 运行流程

### 启动顺序：
1. **启动Python智能体服务**
   ```bash
   cd agent-service
   python -m stagex2.api  # 或 uvicorn stagex2.api:app --port 8001
   ```

2. **启动Java后端**（如需要）
   ```bash
   mvn spring-boot:run  # 或 java -jar xxx.jar
   ```

3. **启动前端开发服务**
   ```bash
   cd frontend
   npm run dev
   ```

### 访问页面：
- 打开浏览器：`http://localhost:5173`
- 导航到智能体交互页面

---

## 🔍 测试连接

### 方式1：使用Mock数据（无需后端）
```env
VITE_API_MODE=mock
```
前端会直接使用本地生成的mock数据

### 方式2：自动回退模式（推荐）
```env
VITE_API_MODE=auto
```
优先调用 `http://localhost:8001/agent/daily-feed`，失败时自动回退到mock

### 方式3：仅调用真实API
```env
VITE_API_MODE=real
```
只调用后端接口，失败则报错

---

## 📊 数据适配器流程

```
Python FastAPI返回 DailyReportResponse
         ↓
前端 http.ts 解析 (applicaton/json)
         ↓
前端 agentAdapter.ts 转换
         ↓
前端 Agent.ts 返回 AgentPageState
         ↓
前端 AgentInteractionPage.vue 渲染
```

---

## ⚠️ 常见问题排查

### 1. 页面显示 "unavailable" 状态
- 检查Python服务是否运行在8001端口
- 检查浏览器Console是否有CORS错误
- 确认 VITE_API_MODE=auto 或 real

### 2. Mock数据能显示但真实API失败
- 检查Python服务的 `/agent/daily-feed` 端点是否正确
- 查看Python服务的日志
- 确认请求格式是否正确

### 3. 网络连接错误
```javascript
// 在浏览器Console中测试连接
fetch('/agent/daily-feed', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    current_price: 100,
    current_volatility: 0.02,
    dealer_inventory: 0,
    steps: 5
  })
})
.then(r => r.json())
.then(d => console.log(d))
.catch(e => console.error(e))
```

---

## ✨ 下一步

1. ✅ 将Python API代码添加到你的FastAPI服务
2. 启动Python服务
3. 刷新前端页面
4. 观察浏览器Network标签，确认请求到达8001
5. 检查返回的数据格式

如有问题，查看前端的Network标签和浏览器Console获取详细错误信息。
