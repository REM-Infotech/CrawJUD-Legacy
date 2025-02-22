import sys
from count_commits import count_branch_commits
from count_lines import count_changed_lines


def check_project_limits() -> None:

    returns1 = count_branch_commits()
    returns2 = count_changed_lines()

    message1 = str(returns1[0])
    commit_count = int(returns1[1])

    message2 = str(returns2[0])
    total_lines_changed = int(returns2[1])


    if total_lines_changed > 500:
        print(f"[ERROR] O número de linhas alteradas ({total_lines_changed}) excede o limite de 500. Revise as mudanças antes de commitar.")
        sys.exit(1)

    elif commit_count > 10 and total_lines_changed > 500:
        print(f"[ERROR] O número de commits ({commit_count}) excede o limite de 10. Considere fazer um rebase.")
        sys.exit(1)

    print(message1)
    print(message2)

if __name__ == "__main__":
    check_project_limits()
