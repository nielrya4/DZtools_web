from applications.stats import run
from flask import render_template


def process_cmd(cmd):
    if cmd == 'help':
        return help()
    elif cmd.startswith('dz_stats '):
        args = cmd[9:]
        if len(args) > 0:
            print(args)
            result = run(args)
            return page_out(result)
    elif cmd == "dz_stats":
        return page_out(render_template("dz_stats/dz_stats.html"))
    elif cmd == "clear":
        return clear()
    elif cmd == "exit":
        return page_out(render_template("index.html"))
    else:
        return not_found(cmd)


def not_found(cmd):
    output = text_out(f"    Command '{cmd}' not found...")
    return output


def help():
    output = text_out(f"    help: show a list of commands \n"
                      f"    clear: Clears the output screen \n"
                      f"    exit: exits the application \n"
                      f"    dz_stats -help: Shows how to use dz_stats command")
    return output


def clear():
    output = text_out("\n\n\n\n\n\n\n\n")
    return output


def text_out(text):
    return "text " + text


def page_out(rendered_template):
    return "page " + rendered_template
