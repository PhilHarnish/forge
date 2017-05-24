import Numberjack

grid = Numberjack.Matrix(3, 3, 1, 99, 'grid')
model = Numberjack.Model(
    # Rows.
    grid[0][0] + grid[0][1] + grid[0][2] == 100,
    grid[1][0] + grid[1][1] + grid[1][2] == 100,
    grid[2][0] + grid[2][1] + grid[2][2] == 100,
    # Columns.
    grid[0][0] + grid[1][0] + grid[2][0] == 100,
    grid[0][1] + grid[1][1] + grid[2][1] == 100,
    grid[0][2] + grid[1][2] + grid[2][2] == 100,
)
targets = [
  [1, 4, 6],
  [8, 5, 7],
  [2, 9, 3],
]

for row in range(0, 3):
  for col in range(0, 3):
    model.add(
        # Ones digit equals target...
        (grid[row][col] % 10 == targets[row][col]) |
        # Tens digit equals target...
        (grid[row][col] - grid[row][col] % 10 == targets[row][col] * 10)
    )

# Solve.
solver = model.load('Mistral')
print('Solution is...')
solver.solve()
for row in range(0, 3):
  print(grid[row])

print('Nodes:', solver.getNodes(), ' Time:', solver.getTime())
