package benchmarks

// go test -benchmem -run=^$ -bench . github.com/philharnish/forge/src/data/graph/bloom/benchmarks

import (
	"encoding/binary"
	"testing"

	"github.com/philharnish/forge/src/data/bits"
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
)

const LAST_POS = mask.SIZE
const MAX_SIZE = 1 << LAST_POS

type MaskIterable uint64

func (m *MaskIterable) NextBit() mask.Mask {
	value := *m
	if value == 0 {
		return 0
	}
	next := value & (value - 1)
	*m = next
	return mask.Mask(value - next)
}

func getLowestSetBit(n int) int {
	mask := 1
	for i := 1; i <= 32; i++ {
		if n&mask > 0 {
			return i
		}
		mask <<= 1
	}
	return 0
}

func getLowestBitTable() [256]int {
	result := [256]int{}
	for i := 0; i < 256; i++ {
		result[i] = getLowestSetBit(i)
	}
	return result
}

var lowestBitTable [256]int = getLowestBitTable()

func runner(b *testing.B, f func(i mask.Mask)) {
	b.Run("sparse", func(b *testing.B) {
		for x := b.N; x >= 0; x-- {
			f(1 << (x % LAST_POS))
		}
	})
	b.Run("dense", func(b *testing.B) {
		for x := b.N; x >= 0; x-- {
			f(1<<(x%LAST_POS) - 1)
		}
	})
}

func BenchmarkOverhead(b *testing.B) {
	positions := uint64(0) // Ensure compiler does not eliminate no-op.
	runner(b, func(i mask.Mask) {
		positions += i
	})
}

func BenchmarkLookupTable(b *testing.B) {
	positions := 0 // Ensure compiler does not eliminate no-op.
	runner(b, func(i mask.Mask) {
		iterator := MaskIterable(i)
		for x := iterator.NextBit(); x > 0; x = iterator.NextBit() {
			b := make([]byte, 4)
			binary.LittleEndian.PutUint32(b, uint32(x))
			if b[0] > 0 {
				positions += lowestBitTable[b[0]]
			} else if b[1] > 0 {
				positions += lowestBitTable[b[1]] + 8
			} else if b[2] > 0 {
				positions += lowestBitTable[b[2]] + 16
			} else {
				positions += lowestBitTable[b[3]] + 24
			}
		}
	})
}

func BenchmarkShiftLookupTable(b *testing.B) {
	positions := 0 // Ensure compiler does not eliminate no-op.
	runner(b, func(i mask.Mask) {
		iterator := MaskIterable(i)
		for x := iterator.NextBit(); x > 0; x = iterator.NextBit() {
			if x <= 0x000000ff {
				positions += lowestBitTable[x&0xff]
			} else if x <= 0x0000ff00 {
				positions += lowestBitTable[(x&0xff00)>>8] + 8
			} else if x <= 0x00ff0000 {
				positions += lowestBitTable[(x&0x00ff0000)>>16] + 16
			} else {
				positions += lowestBitTable[(x&0xff000000)>>24] + 24
			}
		}
	})
}

var deBruijnBitPosition = [32]byte{
	0, 1, 28, 2, 29, 14, 24, 3, 30, 22, 20, 15, 25, 17, 4, 8,
	31, 27, 13, 23, 21, 19, 16, 7, 26, 12, 18, 6, 11, 5, 10, 9,
}

func BenchmarkDeBruijn(b *testing.B) {
	positions := 0 // Ensure compiler does not eliminate no-op.
	runner(b, func(i mask.Mask) {
		iterator := MaskIterable(i)
		for i := iterator.NextBit(); i > 0; i = iterator.NextBit() {
			positions += int(deBruijnBitPosition[(uint32)(i*0x077CB531)>>27])
		}
	})
}

func BenchmarkIterate(b *testing.B) {
	positions := 0 // Ensure compiler does not eliminate no-op.
	runner(b, func(i mask.Mask) {
		for x := 0; x < LAST_POS; x++ {
			if i&(1<<i) > 0 {
				positions += x
			}
		}
	})
}

func BenchmarkIterateWithEarlyExit(b *testing.B) {
	positions := 0 // Ensure compiler does not eliminate no-op.
	runner(b, func(i mask.Mask) {
		remaining := i
		for x := 0; x < LAST_POS; x++ {
			cursor := mask.Mask(1 << x)
			if i&cursor > 0 {
				positions += x
				remaining -= cursor
				if remaining == 0 {
					break
				}
			}
		}
	})
}

func BenchmarkC(b *testing.B) {
	positions := 0 // Ensure compiler does not eliminate no-op.
	runner(b, func(i mask.Mask) {
		iterator := MaskIterable(i)
		for x := iterator.NextBit(); x > 0; x = iterator.NextBit() {
			result, err := bits.FindFirstSet(uint32(i))
			if err != nil {
				panic(err)
			}
			positions += result
		}
	})
}
