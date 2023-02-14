#!/usr/bin/python3

import argparse
import sys

from network import TCPServer, TCPClient
from gui import ChatGui


def arg_parser():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--no-use-rsa",
        action="store_true",
        help="Disable RSA (Should be the same on both side)",
    )
    parser.add_argument(
        "-s", "--server", action="store_true", help="Run the app as the server"
    )
    parser.add_argument(
        "--no-default",
        action="store_false",
        help="Run the app with default when not used",
    )

    subparsers = parser.add_subparsers(help="types of interface")
    gui_parser = subparsers.add_parser("gui")
    gui_parser.set_defaults(which="gui")

    cli_parser = subparsers.add_parser("cli")
    cli_parser.add_argument("--host", help="The host address", default="localhost")
    cli_parser.add_argument(
        "-p", "--port", type=int, help="The port for the communication", default=8790
    )
    cli_parser.set_defaults(which="cli")

    args = parser.parse_args()
    if not hasattr(args, "which"):
        parser.print_help(sys.stderr)
        sys.exit(1)

    return args


if __name__ == "__main__":
    args = arg_parser()
    socket = None
    if args.which == "gui":
        socket = ChatGui(
            use_rsa=not args.no_use_rsa, is_server=args.server, default=args.no_default
        )
        socket.mainloop()
    else:
        if args.server:
            socket = TCPServer(
                args.host, args.port, use_rsa=not args.no_use_rsa, is_cli=True
            )
        else:
            socket = TCPClient(
                args.host, args.port, use_rsa=not args.no_use_rsa, is_cli=True
            )
        socket.run()
