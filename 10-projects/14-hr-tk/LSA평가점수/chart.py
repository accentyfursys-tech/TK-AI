import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터
names = ['곽현서', '안덕찬', '이예나', '박정인', '나원빈', '최시원',
         '김예서', '서재현', '손창환', '채형우', '손희정', '김창석', '김강욱', '권예지']

scores = {
    '곽현서':  [95.1, 81.8, 73.2, 93.14, 94.17, 80.88, 84.69],
    '안덕찬':  [87.8, 84.4, 90.2, 76.92, 74.76, 73.53, 83.67],
    '이예나':  [76.8, 75.3, 76.8, 78.46, 68.93, 98.53, 85.71],
    '박정인':  [57.3, 77.9, 89.0, None,  75.73, 94.12, 81.63],
    '나원빈':  [75.6, 83.1, 76.8, 76.92, 65.05, 66.18, 73.47],
    '최시원':  [63.4, 85.7, 68.3, 78.65, 66.99, 83.82, 70.41],
    '김예서':  [80.5, 68.8, 61.0, 75.38, 63.11, 69.12, 75.51],
    '서재현':  [78.0, 63.6, 68.3, 65.67, 60.19, 82.35, 71.43],
    '손창환':  [87.8, 54.5, 39.0, 63.38, 76.70, 70.59, 70.41],
    '채형우':  [54.9, 59.7, 67.1, 77.46, 60.68, 76.96, 71.43],
    '손희정':  [68.3, 68.8, 65.9, 52.31, 57.28, 67.16, 83.67],
    '김창석':  [75.6, 57.1, 54.9, 81.54, 51.46, 67.65, 65.31],
    '김강욱':  [72.0, 71.4, 30.5, 53.97, 47.57, 77.94, 55.10],
    '권예지':  [46.3, 59.7, 34.1, 63.08, 33.98, 50.00, 37.76],
}

차시 = ['1차시', '2차시', '3차시', '4차시', '5차시', '6차시', '7차시']
x = np.arange(1, 8)

# 평균 계산
def avg(v):
    vals = [s for s in v if s is not None]
    return round(sum(vals) / len(vals), 1)

averages = {n: avg(s) for n, s in scores.items()}
sorted_names = sorted(names, key=lambda n: averages[n], reverse=True)

# 색상 그룹 (평균 기준)
def get_color(name):
    a = averages[name]
    if a >= 78:   return '#FF6B6B'   # 상위 - 빨강 계열
    elif a >= 68: return '#4ECDC4'   # 중위 - 청록
    else:         return '#95A5A6'   # 하위 - 회색

# ── 차트 1: 전체 추이 라인차트 ──────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))

for name in sorted_names:
    s = scores[name]
    xs = [x[i] for i in range(7) if s[i] is not None]
    ys = [s[i] for i in range(7) if s[i] is not None]
    color = get_color(name)
    ax.plot(xs, ys, marker='o', label=f'{name} (평균 {averages[name]})', color=color, linewidth=1.8, markersize=5)

ax.set_xticks(x)
ax.set_xticklabels(차시, fontsize=11)
ax.set_ylabel('점수', fontsize=12)
ax.set_title('LSA 평가 점수 추이 (1~7차시)', fontsize=15, fontweight='bold', pad=15)
ax.set_ylim(20, 105)
ax.axhline(y=75, color='gray', linestyle='--', alpha=0.4, label='75점 기준선')
ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=9, borderaxespad=0)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('C:/iloom-workspace/10-projects/14-hr-tk/LSA평가점수/chart_trend.png', dpi=150, bbox_inches='tight')
plt.close()
print("차트1 저장 완료")

# ── 차트 2: 차시별 점수 히트맵 ────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 8))

matrix = []
for name in sorted_names:
    row = [s if s is not None else np.nan for s in scores[name]]
    matrix.append(row)

matrix_np = np.array(matrix, dtype=float)
im = ax.imshow(matrix_np, cmap='RdYlGn', aspect='auto', vmin=30, vmax=100)

ax.set_xticks(range(7))
ax.set_xticklabels(차시, fontsize=11)
ax.set_yticks(range(len(sorted_names)))
ax.set_yticklabels([f'{n} ({averages[n]})' for n in sorted_names], fontsize=10)
ax.set_title('LSA 평가 점수 히트맵 (평균 순 정렬)', fontsize=14, fontweight='bold', pad=15)

for i in range(len(sorted_names)):
    for j in range(7):
        val = matrix_np[i, j]
        if not np.isnan(val):
            ax.text(j, i, f'{val:.1f}', ha='center', va='center', fontsize=8,
                    color='black' if 40 < val < 85 else 'white')

plt.colorbar(im, ax=ax, label='점수')
plt.tight_layout()
plt.savefig('C:/iloom-workspace/10-projects/14-hr-tk/LSA평가점수/chart_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("차트2 저장 완료")

# ── 차트 3: 인원별 평균 점수 바차트 ──────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))

bar_colors = [get_color(n) for n in sorted_names]
bars = ax.bar(range(len(sorted_names)), [averages[n] for n in sorted_names], color=bar_colors, edgecolor='white', linewidth=0.8)

for i, (name, bar) in enumerate(zip(sorted_names, bars)):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{averages[name]}', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xticks(range(len(sorted_names)))
ax.set_xticklabels(sorted_names, fontsize=10, rotation=15)
ax.set_ylabel('평균 점수', fontsize=12)
ax.set_title('인원별 평균 점수 (1~7차시)', fontsize=14, fontweight='bold', pad=15)
ax.set_ylim(0, 105)
ax.axhline(y=75, color='gray', linestyle='--', alpha=0.5, label='75점 기준')
ax.axhline(y=65, color='orange', linestyle='--', alpha=0.5, label='65점 기준')
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)

from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#FF6B6B', label='상위 (평균 78+)'),
                   Patch(facecolor='#4ECDC4', label='중위 (68~78)'),
                   Patch(facecolor='#95A5A6', label='하위 (~68)')]
ax.legend(handles=legend_elements, loc='upper right', fontsize=9)

plt.tight_layout()
plt.savefig('C:/iloom-workspace/10-projects/14-hr-tk/LSA평가점수/chart_avg.png', dpi=150, bbox_inches='tight')
plt.close()
print("차트3 저장 완료")
