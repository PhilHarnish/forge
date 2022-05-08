package node

type NodeIterator interface {
	Items(acceptor NodeAcceptor) NodeItems
	Root() *Node
	String() string
}
