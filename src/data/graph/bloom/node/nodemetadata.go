package node

import "github.com/philharnish/forge/src/data/graph/bloom/weight"

type NodeMetadata = []*weight.WeightedString

type NodeMetadataProvider interface {
	Metadata(paths []string, items []NodeItems) NodeMetadata
}
