// 예시: 구 S와 평면 α, 원 C 위의 점 P (기하 30번)
// 좌표 규약: z축이 위쪽, 평면 α는 z = 0
const s2 = Math.SQRT2;

export const DEMO_IMAGE = "sample-30.jpg";

export const DEMO_SCENE = {
  title: "구 S와 정사영 (기하 30번)",
  problem:
    "반지름의 길이가 5인 구 $S$와 평면 $\\alpha$가 만나서 생기는 원 $C$ 위의 점 $\\mathrm{P}$와, 평면 $\\alpha$ 위에 있지 않고 구 $S$ 위에 있는 두 점 $\\mathrm{Q},\\mathrm{R}$이 다음을 만족한다.\n\n(가) $\\overline{\\mathrm{PR}}=10$이고, 점 $\\mathrm{Q}$와 평면 $\\alpha$ 사이의 거리는 4이다.\n(나) 평면 $\\mathrm{PQR}$과 원 $C$는 점 $\\mathrm{P}$에서만 만난다.\n(다) 원 $C$의 평면 $\\mathrm{PQR}$ 위로의 정사영의 넓이는 $\\frac{64}{5}\\pi$이다.\n\n직선 $\\mathrm{QR}$과 평면 $\\alpha$가 이루는 예각을 $\\theta$라 할 때, $\\sin^2\\theta=\\frac{q}{p}$이다. $p+q$의 값은?",
  points: [
    { name: "O", coord: [0, 0, 3], showLabel: true },
    { name: "M", coord: [0, 0, 0], showLabel: true },
    { name: "P", coord: [4, 0, 0], showLabel: true },
    { name: "Q", coord: [-4 / 3, (10 * s2) / 3, 4], showLabel: true },
    { name: "R", coord: [-4, 0, 6], showLabel: true },
    { name: "H", coord: [-4 / 3, (10 * s2) / 3, 0], showLabel: true },
    { name: "R'", coord: [-4, 0, 0], showLabel: true },
  ],
  segments: [
    { id: "PQ", from: "P", to: "Q", style: "solid", color: "#e2554f" },
    { id: "QR", from: "Q", to: "R", style: "solid", color: "#e2554f" },
    { id: "PR", from: "P", to: "R", style: "solid", color: "#e2554f" },
    { id: "OM", from: "O", to: "M", style: "dashed", color: "#8a8f98" },
    { id: "MP", from: "M", to: "P", style: "dashed", color: "#8a8f98" },
    { id: "OP", from: "O", to: "P", style: "dashed", color: "#8a8f98" },
    { id: "QH", from: "Q", to: "H", style: "dashed", color: "#2f9e6f" },
    { id: "RR'", from: "R", to: "R'", style: "dashed", color: "#2f9e6f" },
  ],
  lines: [
    { id: "l", label: "ℓ (접선)", point: [4, 0, 0], direction: [0, 1, 0], color: "#d68a00" },
  ],
  polygons: [
    { id: "tri", vertices: ["P", "Q", "R"], color: "#e2554f", opacity: 0.18 },
  ],
  planes: [
    { id: "alpha", label: "α", point: [0, 0, 0], normal: [0, 0, 1], size: 16, color: "#4c7bd9" },
    { id: "PQR", label: "평면 PQR", point: [0, 0, 3], normal: [3, 0, 4], size: 14, color: "#e2554f" },
  ],
  spheres: [{ id: "S", label: "S", center: [0, 0, 3], radius: 5, color: "#7c8cff" }],
  circles: [
    { id: "C", label: "C", center: [0, 0, 0], normal: [0, 0, 1], radius: 4, color: "#4c7bd9", style: "solid" },
  ],
  projections: [{ id: "Cproj", label: "C의 정사영", sourceId: "C", planeId: "PQR", color: "#d68a00" }],
  steps: [
    {
      title: "1. PR은 구의 지름",
      explanation:
        "구의 반지름이 5이므로 지름은 10이다. $\\overline{\\mathrm{PR}}=10$이므로 $\\mathrm{PR}$은 지름이고, 구의 중심 $\\mathrm{O}$는 선분 $\\mathrm{PR}$의 중점이다.\n\n따라서 **평면 PQR은 구의 중심 O를 지난다.** 평면 PQR과 구의 교선은 반지름 5인 대원이다.",
      highlight: ["PR", "O", "P", "R", "S"],
      view: "iso",
    },
    {
      title: "2. (나) → 평면 PQR ∩ α 는 원 C의 접선",
      explanation:
        "평면 PQR과 원 $C$가 점 P에서만 만나므로, 두 평면 PQR과 $\\alpha$의 교선 $\\ell$은 원 $C$에 P에서 접한다.\n\n원 $C$의 중심을 M이라 하면 $\\overline{\\mathrm{MP}}\\perp\\ell$이고 $\\overline{\\mathrm{OM}}\\perp\\alpha$이므로, **삼수선의 정리**에 의해 $\\overline{\\mathrm{OP}}\\perp\\ell$.",
      highlight: ["l", "MP", "OM", "OP", "C", "PQR", "alpha"],
      view: "iso",
    },
    {
      title: "3. 두 평면이 이루는 각",
      explanation:
        "$\\ell$에 수직인 두 직선 MP(평면 α 위), OP(평면 PQR 위)가 이루는 각 $\\angle\\mathrm{OPM}=\\varphi$가 두 평면의 이면각이다.\n\n원 $C$의 반지름을 $r$이라 하면 $\\overline{\\mathrm{MP}}=r,\\ \\overline{\\mathrm{OP}}=5$이므로\n$$\\cos\\varphi=\\frac{r}{5}$$\n\n💡 ℓ 방향으로 보면(측면 보기) 각 OPM이 그대로 보인다.",
      highlight: ["MP", "OP", "OM", "O", "M", "P"],
      view: "front",
    },
    {
      title: "4. (다) 정사영 넓이 → r = 4",
      explanation:
        "원 $C$의 넓이는 $\\pi r^2$이고, 정사영의 넓이는\n$$\\pi r^2\\cos\\varphi=\\pi r^2\\cdot\\frac{r}{5}=\\frac{64}{5}\\pi$$\n이므로 $r^3=64,\\ r=4$. 따라서 $\\overline{\\mathrm{OM}}=\\sqrt{25-16}=3$.\n\n주황색 타원이 평면 PQR 위로의 정사영이다. (평면 PQR에 수직으로 보면 타원 모양이 그대로 보인다.)",
      highlight: ["C", "Cproj", "PQR"],
      view: "normal:PQR",
    },
    {
      title: "5. 좌표로 Q 구하기",
      explanation:
        "$\\mathrm{M}(0,0,0),\\ \\mathrm{O}(0,0,3),\\ \\mathrm{P}(4,0,0)$, $\\alpha: z=0$으로 두면 $\\mathrm{R}=2\\mathrm{O}-\\mathrm{P}=(-4,0,6)$.\n\n평면 PQR은 $\\ell$(y축 방향)과 O를 지나므로 $3x+4z=12$.\n\nQ는 평면 α와의 거리가 4: $z=4$이면 $x=-\\tfrac43$, 구의 방정식 $x^2+y^2+(z-3)^2=25$에서 $y^2=\\tfrac{200}{9}$.\n($z=-4$이면 $x=\\tfrac{28}{3}>5$이므로 불가능)\n$$\\mathrm{Q}\\left(-\\tfrac43,\\ \\tfrac{10\\sqrt2}{3},\\ 4\\right)$$",
      highlight: ["Q", "QH", "H", "PQR", "S"],
      view: "iso",
    },
    {
      title: "6. sin²θ 계산",
      explanation:
        "$\\overrightarrow{\\mathrm{QR}}=\\left(-\\tfrac83,\\ -\\tfrac{10\\sqrt2}{3},\\ 2\\right)$이므로\n$$|\\overline{\\mathrm{QR}}|^2=\\frac{64}{9}+\\frac{200}{9}+4=\\frac{100}{3}$$\n직선 QR과 평면 α가 이루는 각에 대해, 높이 차는 $6-4=2$이므로\n$$\\sin^2\\theta=\\frac{2^2}{100/3}=\\frac{3}{25}$$\n$p=25,\\ q=3$ → $p+q=28$.",
      highlight: ["QR", "Q", "R", "QH", "RR'", "alpha"],
      view: "front",
    },
  ],
  answer: "28",
};
