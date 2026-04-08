from .task import Task


class TaskList(list[Task]): # TaskList class using composition with the Task class.
    
    def __repr__(self):
        out = "TaskList:\n"
        out += Task.format_header_row("NAME", "TYPE", "VERSION", "MODIFIED") + "\n"
        for task in self:
            out += f"{task}\n"

        return out
    