from srk_report import Event
from get_errors import get_errors


def main():
    errors = get_errors(day=5, test=True)
    print(errors)


if __name__ == '__main__':
    main()
