from count_commits import count_branch_commits
from count_lines import count_changed_lines


def check_project_limits() -> None:

    message1 = count_branch_commits()
    message2 = count_changed_lines()

    print(message1)
    print(message2)

if __name__ == "__main__":
    check_project_limits()
