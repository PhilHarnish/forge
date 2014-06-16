package main

import (
	_ "net/http/pprof"
	"net/http"
	"fmt"
	"euler/go_euler"
)

func main() {
	fmt.Println("Hello world.")
	go func() {
		fmt.Println(http.ListenAndServe("localhost:6060", nil))
	}()
	n := 2000000
	sum := 0
	/*
	f := go_euler.Primes()
	i := 0
	for next := <-f; next < n; next = <-f {
		go_euler.GeneratePrime(i + 5)
		i++
		sum += next
	}
	*/
	for i := 0; i < n; i++ {
		go go_euler.GeneratePrime(i + 5)
	}
	fmt.Println("Result:", sum)
	//go_euler.GeneratePrime(n)
}
