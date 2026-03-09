export interface GraphNode {
  id: string;
  label: string;
  x: number;
  y: number;
  color: string;
}

export interface GraphEdge {
  from: string;
  to: string;
  weight: number;
}

export const mockExplainGraphs: Record<string, { nodes: GraphNode[]; edges: GraphEdge[] }> = {
  "Model-1": {
    nodes: [
      { id: "USD/CNY", label: "USD/CNY", x: 80, y: 120, color: "#4f82ff" },
      { id: "EUR/CNY", label: "EUR/CNY", x: 220, y: 70, color: "#2fc3ff" },
      { id: "JPY/CNY", label: "JPY/CNY", x: 240, y: 190, color: "#6a5eff" },
      { id: "WTI", label: "WTI", x: 380, y: 120, color: "#ff8b5f" }
    ],
    edges: [
      { from: "USD/CNY", to: "EUR/CNY", weight: 0.72 },
      { from: "USD/CNY", to: "JPY/CNY", weight: 0.64 },
      { from: "EUR/CNY", to: "WTI", weight: 0.58 },
      { from: "JPY/CNY", to: "WTI", weight: 0.67 }
    ]
  },
  "Model-2": {
    nodes: [
      { id: "USD/CNY", label: "USD/CNY", x: 80, y: 80, color: "#4f82ff" },
      { id: "EUR/CNY", label: "EUR/CNY", x: 220, y: 140, color: "#2fc3ff" },
      { id: "JPY/CNY", label: "JPY/CNY", x: 160, y: 240, color: "#6a5eff" },
      { id: "WTI", label: "WTI", x: 360, y: 170, color: "#ff8b5f" }
    ],
    edges: [
      { from: "USD/CNY", to: "WTI", weight: 0.49 },
      { from: "EUR/CNY", to: "WTI", weight: 0.62 },
      { from: "JPY/CNY", to: "EUR/CNY", weight: 0.51 },
      { from: "JPY/CNY", to: "WTI", weight: 0.55 }
    ]
  }
};
