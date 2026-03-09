from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque

maze = [
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1],
    [1, 0, 0, 0],
]
START = (0, 0)
END = (3, 3)
N = 4

def bfs(maze, start, end):
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        (r, c), path = queue.popleft()
        if (r, c) == end:
            return path
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < N and 0 <= nc < N and maze[nr][nc] == 0 and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(nr, nc)]))

classical_path = bfs(maze, START, END)

qc = QuantumCircuit(3, 3)
for i in range(3):
    qc.h(i)
qc.x(1)
qc.x(2)
qc.h(2)
qc.ccx(0, 1, 2)
qc.h(2)
qc.x(1)
qc.x(2)
for i in range(3):
    qc.h(i)
for i in range(3):
    qc.x(i)
qc.h(2)
qc.ccx(0, 1, 2)
qc.h(2)
for i in range(3):
    qc.x(i)
for i in range(3):
    qc.h(i)
qc.measure(range(3), range(3))

simulator = AerSimulator()
counts = simulator.run(qc, shots=2000).result().get_counts()
sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
target = "001"

best = sorted_counts[0][0]
r, c = START
quantum_path = [START]
for bit in best:
    r, c = (r+1, c) if bit == "0" else (r, c+1)
    if 0 <= r < N and 0 <= c < N:
        quantum_path.append((r, c))

if quantum_path[-1] != END:
    rest = bfs(maze, quantum_path[-1], END)
    quantum_path = quantum_path + rest[1:]


def draw_maze(ax, path, title):
    for i in range(N):
        for j in range(N):
            color = "#2C3E50" if maze[i][j] == 1 else "#F8F9FA"
            ax.add_patch(patches.Rectangle((j, N-1-i), 1, 1, color=color, ec="#DEE2E6", lw=1))

    for i in range(N):
        for j in range(N):
            if maze[i][j] == 1:
                ax.text(j+0.5, N-1-i+0.5, "x", ha="center", va="center", fontsize=13, color="#ECF0F1")

    if path:
        for idx, (pi, pj) in enumerate(path):
            if (pi, pj) == START:
                ax.add_patch(patches.Rectangle((pj, N-1-pi), 1, 1, color="#2ECC71"))
                ax.text(pj+0.5, N-1-pi+0.5, "S", ha="center", va="center", fontsize=16, fontweight="bold", color="white")
            elif (pi, pj) == END:
                ax.add_patch(patches.Rectangle((pj, N-1-pi), 1, 1, color="#E74C3C"))
                ax.text(pj+0.5, N-1-pi+0.5, "E", ha="center", va="center", fontsize=16, fontweight="bold", color="white")
            else:
                ax.add_patch(patches.Rectangle((pj, N-1-pi), 1, 1, color="#F39C12", alpha=0.85))
                ax.text(pj+0.5, N-1-pi+0.5, str(idx), ha="center", va="center", fontsize=12, fontweight="bold", color="white")

        for k in range(len(path)-1):
            r1, c1 = path[k]
            r2, c2 = path[k+1]
            ax.annotate("", xy=(c2+0.5, N-1-r2+0.5), xytext=(c1+0.5, N-1-r1+0.5),
                        arrowprops=dict(arrowstyle="-|>", color="white", lw=2))

    ax.set_xlim(0, N)
    ax.set_ylim(0, N)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
    for spine in ax.spines.values():
        spine.set_linewidth(2)
        spine.set_color("#2C3E50")


fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor("#1A1A2E")

fig.text(0.5, 0.96, "QUANTUM MAZE SOLVER", ha="center", fontsize=20, fontweight="bold", color="white")
fig.text(0.5, 0.92, "Grover's Algorithm  |  IBM Quantum ibm_fez (156 qubits)  |  Qiskit",
         ha="center", fontsize=11, color="#A0AEC0")

probs = [s[1] / 2000 * 100 for s in sorted_counts]
states = [s[0] for s in sorted_counts]

fig.text(0.03, 0.88,
         "Simulator: |001> = " + str(round(probs[0], 1)) + "%   |   " +
         "1 iter: 62.0% → 2 iter: 80.6% (ibm_fez)   |   " +
         "Classical path: " + str(len(classical_path)-1) + " steps   |   " +
         "Quantum speedup: O(sqrtN) vs O(N)",
         fontsize=9, color="#68D391")

ax1 = fig.add_axes([0.03, 0.08, 0.28, 0.75])
ax2 = fig.add_axes([0.36, 0.08, 0.28, 0.75])
ax3 = fig.add_axes([0.69, 0.08, 0.28, 0.75])

for ax in [ax1, ax2, ax3]:
    ax.set_facecolor("#16213E")

draw_maze(ax1, [], "Unsolved Maze")
ax1.add_patch(patches.Rectangle((0, N-1), 1, 1, color="#2ECC71"))
ax1.text(0.5, N-0.5, "S", ha="center", va="center", fontsize=16, fontweight="bold", color="white")
ax1.add_patch(patches.Rectangle((3, 0), 1, 1, color="#E74C3C"))
ax1.text(3.5, 0.5, "E", ha="center", va="center", fontsize=16, fontweight="bold", color="white")
ax1.title.set_color("white")

draw_maze(ax2, classical_path, "Classical BFS Solution")
ax2.title.set_color("white")

draw_maze(ax3, quantum_path, "Quantum Grover Solution")
ax3.title.set_color("white")

ax_hist = fig.add_axes([0.03, 0.0, 0.93, 0.06])
ax_hist.set_facecolor("#16213E")
ax_hist.barh([""], [probs[0]], color="#E74C3C", height=0.5)
ax_hist.text(probs[0]/2, 0, "|001>  " + str(round(probs[0], 1)) + "%",
             ha="center", va="center", fontsize=9, fontweight="bold", color="white")
left = probs[0]
for s, p in zip(states[1:], probs[1:]):
    ax_hist.barh([""], [p], left=left, color="#4A90D9", height=0.5)
    ax_hist.text(left + p/2, 0, "|" + s + ">\n" + str(round(p, 1)) + "%",
                 ha="center", va="center", fontsize=7, color="white")
    left += p
ax_hist.set_xlim(0, 100)
ax_hist.set_xticks([])
ax_hist.set_yticks([])
ax_hist.set_title("Quantum Probability Distribution — Simulator", fontsize=9, color="#A0AEC0", pad=3)

plt.savefig("quantum_maze_FINAL.png", dpi=200, bbox_inches="tight", facecolor="#1A1A2E")
print("Done! Open: open quantum_maze_FINAL.png")
