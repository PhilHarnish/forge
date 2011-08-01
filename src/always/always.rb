#!/usr/bin/env ruby

require 'rubygems'
require 'sinatra'

def fcsh()
  # Open fcsh for read/write
  fd = IO.popen("fcsh", "w+")

  fd
end

def read(fd)
  fd.flush

  buffer = ""
  while c = fd.read(1)
    buffer += c
    if /^\(fcsh\) / =~ buffer
      break
    end
  end
  stdout(buffer)
end

def write(fd, str)
  fd.puts str
  read(fd)
end

def stdout(str)
  $stdout.puts str
  $stdout.flush
end

$fd = fcsh()

def quit()
  $fd.close
  exit
end

read($fd)

Signal.trap(:INT) {
  quit
}

get '/' do
  'hello world'
end

get '/build' do
  write($fd, "mxmlc -debug=true -target-player=10.2.0 -o=web/latest.swf -compiler.source-path=flash flash/ichigo/Main.as")
  send_file 'web/latest.swf'
end

get '/quit' do
  quit
  'quit'
end
