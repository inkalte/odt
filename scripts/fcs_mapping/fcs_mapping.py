from misc import load_csv


def main():
    new_list = list(load_csv('./input_new.csv'))

    for old in load_csv('./input_old.csv'):
        for n, new in enumerate(new_list):
            if old[2] == new[2]:
                print(f'/usr/ios/cli/ioscli vfcmap -vadapter {new[0]} -fcp {old[4]};')
                new_list.pop(n)
                break


if __name__ == '__main__':
    main()
