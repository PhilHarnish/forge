package go_euler

func Problem14(n int) int {
	lengths := make([]int, n)
	lengths[1] = 1
	largest := 0
	longest := 1
	history := make([]int, 1024) // ~550 needed for n = 1M.
	for i := 2; i < n; i++ {
		if lengths[i] > 0 {
			// Already visited, return.
			continue
		}
		current := i
		// Truncate history.
		history = history[:0]
		distance := 0
		// Iterate past any number greater than n until a known distance is found.
		for current >= n || lengths[current] == 0 {
			history = append(history, current)
			distance++
			if current%2 == 0 {
				current /= 2
			} else {
				current = (3*current + 1) / 2
			}
		}
		distance += lengths[current]
		if distance > largest {
			largest = distance
			longest = i
		}
		for backfill := 0; backfill < len(history); backfill++ {
			current = history[backfill]
			if current < n {
				// Only save distances less than n.
				lengths[current] = distance
			}
			distance--
		}
	}
	return longest
}
