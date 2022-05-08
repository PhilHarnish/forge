package node

type NodeIterator interface {
	Items(generator NodeGenerator) NodeItems
	Root() *Node
	String() string
}
