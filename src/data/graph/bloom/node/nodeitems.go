package node

type NodeItems interface {
	HasNext() bool
	Next() (string, NodeIterator)
}
