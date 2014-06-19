package go_euler

type Vector struct {
	X int
	Y int
}

func Problem11(input *[][]int, length int) int {
	// Largest `length` product in input.
	directions := [][]Vector{
		{{1, 0}, {0, 1}},  // Rows first. Increment col on wrap.
		{{0, 1}, {1, 0}},  // Cols first. Increment row on wrap.
		{{1, 1}, {1, 0}},  // South-east diagonal. Move +1 col on wrap.
		{{-1, 1}, {1, 0}},  // South-west diagonal. Move +1 col on wrap.
	}
	// Sentinel channel for merging.
  products := make(chan int)
	close(products)
	for _, direction := range directions {
		stream := make(chan int)
		go inputStream(input, direction[0], direction[1], stream)
		products = Merge(products, ChainMultiply(stream, length))
	}
	return Max(products)
}

// Traverses input according to dir, applies offset after reading a block.
// Outputs numbers on `out` and 0 when exiting the table.
func inputStream(input *[][]int, dir Vector, offset Vector, out chan int) {
	table := *input
	row := 0
	rows := len(table)
	col := 0
	cols := len(table[row])
	batch := 0
	for remaining := rows * cols; remaining > 0; remaining-- {
		out <- table[row][col]
		batch++
		row += dir.Y
		col += dir.X
		if batch == cols {
			col += offset.X
			row += offset.Y
			batch = 0
		}
		if col >= cols || col < 0 {
			col = (col + cols) % cols
			out <- 0
		}
		if row >= rows || row < 0 {
			row = (row + rows) % rows
			out <- 0
		}
	}
	close(out)
}
