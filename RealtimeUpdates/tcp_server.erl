-module(tcp_server).
-export([start/0, loop/1]).

start() ->
    {ok, ListenSocket} = gen_tcp:listen(12345, [binary, {packet, 0}, {active, false}, {reuseaddr, true}]),
    loop(ListenSocket).

loop(ListenSocket) ->
    {ok, Socket} = gen_tcp:accept(ListenSocket),
    {ok, Bin} = gen_tcp:recv(Socket, 0),
    io:format("Received ~p~n", [Bin]),
    gen_tcp:close(Socket),
    loop(ListenSocket).