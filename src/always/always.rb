#!/usr/bin/env ruby

require 'rubygems'
require 'sinatra'

$files = {
  'web/latest.swf' => "mxmlc -debug=true -target-player=10.2.0 -o=web/latest.swf -compiler.source-path=flash flash/ichigo/Main.as"
}

$targets = {}

def fcsh_read(fd)
  fd.flush

  buffer = ""
  while buffer += fd.read(1) and ! (/^\(fcsh\) / =~ buffer)
  end
  print buffer
  buffer
end

def fcsh_write(fd, str)
  print str
  fd.puts str
  fcsh_read(fd)
end

def build(fd, cmd)
  if $targets[cmd]
    fcsh_write(fd, "compile %d" % $targets[cmd])
  else
    buffer = fcsh_write(fd, cmd)
    if /Assigned ([\d+]) as the compile target id/ =~ buffer
      $targets[cmd] = $1
    end
  end
end

$fd = IO.popen("fcsh", "w+")
fcsh_read($fd)

get '/*' do |path|
  if $files[path]
    build($fd, $files[path])
  end

  send_file path
end
